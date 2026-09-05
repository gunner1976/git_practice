import * as THREE from 'three';
import type { TissueParams } from './types';

/**
 * One MeshPhysicalMaterial per tissue class, shared by every organ of that class.
 * The glTF carries baked albedo / roughness / normal tiles per class; here we add
 * what glTF cannot express: the subsurface term, specular occlusion from the
 * per-organ AO (COLOR_0), and the tint the manifest asks for.
 *
 * Subsurface: the screen-space pass (sss.ts) blurs the lit colour where a mask
 * pass (one flat colour per organ, see `sssMaskMaterial`) says the tissue
 * scatters; this material adds a cheap wrapped, back-scattered diffuse term so
 * thin tissue (ears, membranes, vessels) transmits light even without the blur.
 */
export interface TissueMaterial extends THREE.MeshPhysicalMaterial {
  userData: { tissue: string; sss: number; sssColor: THREE.Color; uniforms?: Record<string, THREE.IUniform> };
}

const cache = new Map<string, TissueMaterial>();

export const sssUniforms = {
  uSSS: { value: 1.0 },                 // global subsurface strength (0 disables the wrap term)
};

export function tissueMaterial(system: string, cls: string, p: TissueParams, base?: THREE.MeshStandardMaterial): TissueMaterial {
  const key = system + ':' + cls;
  const hit = cache.get(key);
  if (hit) return hit;
  const m = new THREE.MeshPhysicalMaterial() as TissueMaterial;
  m.name = 'tissue_' + system + '_' + cls;
  if (base) {
    m.map = base.map;
    m.roughnessMap = base.roughnessMap;
    m.normalMap = base.normalMap;
    m.normalScale.copy(base.normalScale);
    m.color.copy(base.color);
  }
  m.roughness = 1.0;                                    // the roughness tile carries the actual value
  m.metalness = 0.0;
  m.specularIntensity = p.specular;
  m.sheen = p.sheen;
  m.sheenRoughness = 0.6;
  m.sheenColor = new THREE.Color(p.sss_color[0], p.sss_color[1], p.sss_color[2]).multiplyScalar(0.6);
  m.clearcoat = p.clearcoat;
  m.clearcoatRoughness = p.coat_rough;
  m.vertexColors = true;                                // COLOR_0 = baked ambient occlusion
  m.side = THREE.FrontSide;
  m.userData = { tissue: cls, sss: p.sss, sssColor: new THREE.Color(...p.sss_color) };

  const uniforms: Record<string, THREE.IUniform> = {
    uSSSColor: { value: m.userData.sssColor },
    uSSSAmount: { value: p.sss },
    uSSS: sssUniforms.uSSS,
    uClipPlane: { value: new THREE.Vector4(0, 0, 0, 0) },   // xyz normal, w distance; zero = off
    uClipOn: { value: 0 },
  };
  m.userData.uniforms = uniforms;

  m.onBeforeCompile = (shader) => {
    Object.assign(shader.uniforms, uniforms);
    shader.vertexShader = shader.vertexShader
      .replace('#include <common>', '#include <common>\nvarying vec3 vWorldPos;')
      .replace('#include <worldpos_vertex>', '#include <worldpos_vertex>\nvWorldPos = (modelMatrix * vec4(transformed, 1.0)).xyz;');
    shader.fragmentShader = shader.fragmentShader
      .replace('#include <common>', `#include <common>
        varying vec3 vWorldPos;
        uniform vec3 uSSSColor; uniform float uSSSAmount; uniform float uSSS; uniform vec4 uClipPlane; uniform float uClipOn;`)
      // COLOR_0 is occlusion, not albedo: do not tint the base colour with it
      .replace('#include <color_fragment>', '')
      // section planes: discard in front of the plane, and draw the cut faces flat so caps read as solid
      .replace('#include <clipping_planes_fragment>', `#include <clipping_planes_fragment>
        if (uClipOn > 0.5 && dot(vWorldPos, uClipPlane.xyz) - uClipPlane.w > 0.0) discard;`)
      // use the baked AO for indirect light and specular occlusion
      .replace('#include <aomap_fragment>', `
        float ambientOcclusion = mix(1.0, vColor.r, 1.0);
        reflectedLight.indirectDiffuse *= ambientOcclusion;
        #if defined( USE_CLEARCOAT )
          clearcoatSpecularIndirect *= ambientOcclusion;
        #endif
        #if defined( USE_SHEEN )
          sheenSpecularIndirect *= ambientOcclusion;
        #endif
        float dotNV = saturate( dot( geometryNormal, geometryViewDir ) );
        reflectedLight.indirectSpecular *= computeSpecularOcclusion( dotNV, ambientOcclusion, material.roughness );`)
      // wrapped + back-scattered diffuse so light bleeds through thin tissue; strength scaled by the class
      .replace('#include <lights_fragment_begin>', `#include <lights_fragment_begin>
        {
          float wrap = 0.35 * uSSSAmount * uSSS;
          vec3 N = normalize(normal);
          #if NUM_DIR_LIGHTS > 0
          for (int i = 0; i < NUM_DIR_LIGHTS; i++) {
            vec3 L = directionalLights[i].direction;
            float nl = dot(N, L);
            float w = saturate((nl + wrap) / (1.0 + wrap)) - saturate(nl);
            float back = pow(saturate(dot(geometryViewDir, -L + N * 0.3)), 6.0) * 0.25 * uSSSAmount * uSSS;
            reflectedLight.directDiffuse += directionalLights[i].color * diffuseColor.rgb * uSSSColor * (w * 0.8 + back);
          }
          #endif
          reflectedLight.indirectDiffuse += diffuseColor.rgb * uSSSColor * 0.06 * uSSSAmount * uSSS * vColor.r;   // vColor.r = baked AO (aomap chunk comes later)
        }`)
      ;
  };
  m.customProgramCacheKey = () => 'tissue-v5';
  cache.set(key, m);
  return m;
}

export function allTissueMaterials(): TissueMaterial[] {
  return [...cache.values()];
}

/** Section plane shared by every tissue material. normal points to the kept side. */
export function setClipPlane(normal: THREE.Vector3 | null, distance = 0) {
  for (const m of cache.values()) {
    const u = m.userData.uniforms!;
    if (!normal) {
      u.uClipOn.value = 0;
    } else {
      // keep the half-space where dot(p, n) - d <= 0
      u.uClipPlane.value.set(normal.x, normal.y, normal.z, distance);
      u.uClipOn.value = 1;
    }
  }
}

/** Flat per-organ subsurface colour/strength, rendered by the SSS pass with scene.overrideMaterial.
 *  Each organ mesh sets `uSSSColor` in onBeforeRender from its tissue material. Honors the section plane. */
export const sssMaskMaterial = new THREE.ShaderMaterial({
  uniforms: { uSSSColor: { value: new THREE.Vector3() }, uClipPlane: { value: new THREE.Vector4() }, uClipOn: { value: 0 } },
  vertexShader: `varying vec3 vWorldPos; void main(){ vec4 wp = modelMatrix * vec4(position, 1.0); vWorldPos = wp.xyz; gl_Position = projectionMatrix * viewMatrix * wp; }`,
  fragmentShader: `uniform vec3 uSSSColor; uniform vec4 uClipPlane; uniform float uClipOn; varying vec3 vWorldPos;
    void main(){ if (uClipOn > 0.5 && dot(vWorldPos, uClipPlane.xyz) - uClipPlane.w > 0.0) discard; gl_FragColor = vec4(uSSSColor, 1.0); }`,
});
export function applyMaskUniforms(mat: TissueMaterial) {
  const u = sssMaskMaterial.uniforms;
  const strength = mat.userData.sss * sssUniforms.uSSS.value * (mat.opacity ?? 1);
  u.uSSSColor.value.set(mat.userData.sssColor.r * strength, mat.userData.sssColor.g * strength, mat.userData.sssColor.b * strength);
  const mu = mat.userData.uniforms!;
  u.uClipPlane.value.copy(mu.uClipPlane.value);
  u.uClipOn.value = mu.uClipOn.value;
}
