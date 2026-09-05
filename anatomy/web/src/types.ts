export interface TissueParams {
  color: [number, number, number];
  roughness: number;
  sss: number;
  sss_color: [number, number, number];
  specular: number;
  sheen: number;
  clearcoat: number;
  coat_rough: number;
  bump: number;
  cavity: number;
  fibrous?: number;
}

export interface OrganEntry {
  id: string;
  name: string;
  source_name: string;
  side: 'l' | 'r' | null;
  system: string;
  parents: string[];
  tissue: string;
  source_material: string;
  optional: boolean;
  tris_source: number;
  tris: number;
  description: string | null;
  bbox: { min: [number, number, number]; max: [number, number, number] };
}

export interface SystemEntry {
  file: string;
  order: number;
  budget: number;
  source: string;
  meshes: number;
  tris: number;
  bytes: number;
  excluded: { name: string; reason: string }[];
}

export interface Manifest {
  generated: string;
  peel_order: string[];
  tissue_classes: Record<string, TissueParams>;
  attribution: string[];
  license: string;
  systems: Record<string, SystemEntry>;
  organs: Record<string, OrganEntry>;
}
