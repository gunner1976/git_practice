import * as THREE from 'three';
import { Pass, FullScreenQuad } from 'three/addons/postprocessing/Pass.js';
import { sssMaskMaterial } from './materials';

/**
 * Screen-space subsurface scattering, after Jimenez et al. (separable SSS):
 * the scene is rendered into a lit-colour target, then once more with a flat override
 * material into a subsurface tint/strength mask, then the lit colour is blurred with a depth-aware, per-channel kernel whose
 * width is a physical scattering radius projected to pixels, and blended back in
 * where the strength buffer says the surface scatters. Red travels the farthest,
 * which is what gives flesh its warm bleeding edges.
 */
export class SSSPass extends Pass {
  private scene: THREE.Scene;
  private camera: THREE.PerspectiveCamera;
  private colorRT: THREE.WebGLRenderTarget;
  private maskRT: THREE.WebGLRenderTarget;
  private tmpA: THREE.WebGLRenderTarget;
  private tmpB: THREE.WebGLRenderTarget;
  private blur: THREE.ShaderMaterial;
  private composite: THREE.ShaderMaterial;
  private quad: FullScreenQuad;
  /** scattering radius in world units (metres); ~4 mm for muscle, tuned globally here */
  radius = 0.004;
  strength = 1.0;
  enabledSSS = true;

  constructor(scene: THREE.Scene, camera: THREE.PerspectiveCamera, width: number, height: number) {
    super();
    this.scene = scene;
    this.camera = camera;
    const depth = new THREE.DepthTexture(width, height, THREE.UnsignedIntType);
    this.colorRT = new THREE.WebGLRenderTarget(width, height, { type: THREE.HalfFloatType, depthTexture: depth });
    this.maskRT = new THREE.WebGLRenderTarget(width, height, { type: THREE.UnsignedByteType });
    this.tmpA = new THREE.WebGLRenderTarget(width, height, { type: THREE.HalfFloatType });
    this.tmpB = new THREE.WebGLRenderTarget(width, height, { type: THREE.HalfFloatType });

    const common = `
      uniform sampler2D tColor; uniform sampler2D tSSS; uniform sampler2D tDepth;
      uniform vec2 uTexel; uniform vec2 uDir; uniform float uNear; uniform float uFar; uniform float uProjScale; uniform float uRadius;
      varying vec2 vUv;
      float linearDepth(float z){ float zn = z * 2.0 - 1.0; return 2.0 * uNear * uFar / (uFar + uNear - zn * (uFar - uNear)); }
    `;
    this.blur = new THREE.ShaderMaterial({
      uniforms: {
        tColor: { value: null }, tSSS: { value: null }, tDepth: { value: null },
        uTexel: { value: new THREE.Vector2(1 / width, 1 / height) }, uDir: { value: new THREE.Vector2(1, 0) },
        uNear: { value: 0.01 }, uFar: { value: 100 }, uProjScale: { value: 1 }, uRadius: { value: 0.004 },
      },
      vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
      fragmentShader: common + `
        void main(){
          vec4 c0 = texture2D(tColor, vUv);
          vec3 s0 = texture2D(tSSS, vUv).rgb;
          float str = max(s0.r, max(s0.g, s0.b));
          if (str < 0.01) { gl_FragColor = c0; return; }
          float d0 = linearDepth(texture2D(tDepth, vUv).r);
          // kernel width in pixels for this depth: radius * (focal length in px) / depth
          float px = uRadius * uProjScale / max(d0, 0.05) * (0.5 + str);
          px = clamp(px, 0.0, 28.0);
          if (px < 0.5) { gl_FragColor = c0; return; }
          // per-channel sigma: red scatters ~2.5x further than blue
          vec3 sigma = vec3(1.0, 0.55, 0.35) * px;
          vec3 sum = c0.rgb; vec3 wsum = vec3(1.0);
          const int N = 10;
          for (int i = 1; i <= N; i++) {
            float x = float(i) * px / float(N) * 2.2;                      // reach out to ~2.2 sigma of the red lobe
            vec3 w = exp(-0.5 * (x * x) / (sigma * sigma));
            for (int s = -1; s <= 1; s += 2) {
              vec2 uv = vUv + uDir * uTexel * x * float(s);
              float d = linearDepth(texture2D(tDepth, uv).r);
              float dz = abs(d - d0) / max(uRadius * 3.0, 1e-4);          // reject across depth discontinuities
              float wd = exp(-dz * dz);
              vec3 ss = texture2D(tSSS, uv).rgb;
              float m = max(ss.r, max(ss.g, ss.b)) > 0.01 ? 1.0 : 0.0;   // only gather from scattering surfaces
              vec3 wi = w * wd * m;
              sum += texture2D(tColor, uv).rgb * wi; wsum += wi;
            }
          }
          gl_FragColor = vec4(sum / wsum, c0.a);
        }`,
    });
    this.composite = new THREE.ShaderMaterial({
      uniforms: { tColor: { value: null }, tBlur: { value: null }, tSSS: { value: null }, uStrength: { value: 1 } },
      vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = vec4(position.xy, 0.0, 1.0); }`,
      fragmentShader: `
        uniform sampler2D tColor; uniform sampler2D tBlur; uniform sampler2D tSSS; uniform float uStrength; varying vec2 vUv;
        void main(){
          vec4 c = texture2D(tColor, vUv); vec3 b = texture2D(tBlur, vUv).rgb; vec3 s = texture2D(tSSS, vUv).rgb;
          // tinted blend: the scattered light takes the tissue's transmission colour
          vec3 mixed = mix(c.rgb, b * (0.85 + 0.3 * s), clamp(s * 1.2, 0.0, 1.0) * uStrength);
          gl_FragColor = vec4(mixed, c.a);
        }`,
    });
    this.quad = new FullScreenQuad(this.blur);
    this.needsSwap = true;
  }

  setSize(w: number, h: number) {
    this.colorRT.setSize(w, h);
    this.maskRT.setSize(w, h);
    this.tmpA.setSize(w, h);
    this.tmpB.setSize(w, h);
    this.blur.uniforms.uTexel.value.set(1 / w, 1 / h);
  }

  render(renderer: THREE.WebGLRenderer, writeBuffer: THREE.WebGLRenderTarget) {
    // 1. lit scene
    renderer.setRenderTarget(this.colorRT);
    renderer.clear();
    renderer.render(this.scene, this.camera);
    const out = this.renderToScreen ? null : writeBuffer;
    if (!this.enabledSSS) {
      this.composite.uniforms.uStrength.value = 0;
      this.composite.uniforms.tColor.value = this.colorRT.texture;
      this.composite.uniforms.tBlur.value = this.colorRT.texture;
      this.composite.uniforms.tSSS.value = this.colorRT.texture;
      this.quad.material = this.composite;
      renderer.setRenderTarget(out);
      this.quad.render(renderer);
      return;
    }
    // 2. subsurface mask: flat tissue transmission colour per organ
    const prevOverride = this.scene.overrideMaterial, prevBg = this.scene.background;
    this.scene.overrideMaterial = sssMaskMaterial;
    this.scene.background = null;
    renderer.setRenderTarget(this.maskRT);
    renderer.setClearColor(0x000000, 0);
    renderer.clear();
    renderer.render(this.scene, this.camera);
    this.scene.overrideMaterial = prevOverride;
    this.scene.background = prevBg;
    const h = this.colorRT.height;
    const focalPx = 0.5 * h / Math.tan(THREE.MathUtils.degToRad(this.camera.fov) * 0.5);
    const u = this.blur.uniforms;
    u.uNear.value = this.camera.near; u.uFar.value = this.camera.far; u.uProjScale.value = focalPx; u.uRadius.value = this.radius;
    u.tSSS.value = this.maskRT.texture; u.tDepth.value = this.colorRT.depthTexture;
    // 3. horizontal
    u.tColor.value = this.colorRT.texture; u.uDir.value.set(1, 0);
    this.quad.material = this.blur;
    renderer.setRenderTarget(this.tmpA); this.quad.render(renderer);
    // 4. vertical
    u.tColor.value = this.tmpA.texture; u.uDir.value.set(0, 1);
    renderer.setRenderTarget(this.tmpB); this.quad.render(renderer);
    // 5. composite
    const c = this.composite.uniforms;
    c.tColor.value = this.colorRT.texture; c.tBlur.value = this.tmpB.texture; c.tSSS.value = this.maskRT.texture; c.uStrength.value = this.strength;
    this.quad.material = this.composite;
    renderer.setRenderTarget(out);
    this.quad.render(renderer);
  }

  get depthTexture() { return this.colorRT.depthTexture!; }

  dispose() {
    this.colorRT.dispose(); this.maskRT.dispose(); this.tmpA.dispose(); this.tmpB.dispose(); this.blur.dispose(); this.composite.dispose(); this.quad.dispose();
  }
}
