// ---------------------------------------------------------------- slide order
import { coreSlides } from './slides_core.js';
import { wellSlides } from './slides_wells.js';

export function buildSlides(ctx) {
  const A = coreSlides(ctx), B = wellSlides(ctx);
  const order = [A.cover, A.goldenlane, A.glance, A.structure, A.seismic, A.marl,
    B.history, B.w6, B.w2, B.w7, B.w9, B.wedge, B.w10, B.t11a, B.t11b,
    B.performance, A.pressure, A.fluids, A.core, A.logs, A.ooip, A.recovery,
    A.opex, A.costs, B.current,
    A.target, A.design, A.risks, A.reserves, A.economics, A.bridge, A.netback, A.commercial, A.close];
  return order.filter(Boolean);
}
