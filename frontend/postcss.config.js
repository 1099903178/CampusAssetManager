/**
 * CampusAssetManager/frontend/postcss.config.js
 * PostCSS 配置文件
 * 
 * 功能说明：
 * - 配置 postcss-px-to-viewport 插件
 * - 实现移动端自适应布局
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

export default {
  plugins: {
    'postcss-px-to-viewport': {
      // 设计稿宽度（单位：px）
      viewportWidth: 375,
      // 视口宽度（单位：vw）
      unitPrecision: 3,
      // 转换后的单位
      viewportUnit: 'vw',
      // 选择器黑名单（不转换的类名）
      selectorBlackList: ['.ignore'],
      // 最小像素值
      minPixelValue: 1,
      // 允许在媒体查询中转换
      mediaQuery: false
    }
  }
}