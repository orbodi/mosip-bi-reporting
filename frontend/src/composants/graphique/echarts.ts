/**
 * Apache ECharts en import modulaire (CLAUDE.md du front) : seuls les graphiques et composants utilisés entrent dans
 * le paquet. Rendu SVG : net à toutes les largeurs et lisible par les outils de test.
 */
import { BarChart, LineChart, MapChart } from 'echarts/charts';
import { GridComponent, TooltipComponent } from 'echarts/components';
import * as echarts from 'echarts/core';
import { SVGRenderer } from 'echarts/renderers';

echarts.use([BarChart, LineChart, MapChart, GridComponent, TooltipComponent, SVGRenderer]);

export { echarts };
export type { ECharts, EChartsCoreOption } from 'echarts/core';
