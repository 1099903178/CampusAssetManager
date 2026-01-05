/**
 * CampusAssetManager/frontend/postcss.config.js
 * PostCSS 配置文件
 * 
 * 功能说明：
 * - 配置 PostCSS 插件
 * - 校物通系统主要面向桌面端，暂不启用移动端适配
 * 
 * 作者：CampusAssetManager开发团队
 * 日期：2026-01-05
 */

export default {
  plugins: {
    // 注释：校物通系统主要面向桌面端，暂时禁用移动端适配
    // 如需启用移动端适配，请取消以下配置并安装 postcss-px-to-viewport
    // 'postcss-px-to-viewport': {
    //   // 设计稿宽度（单位：px）
    //   viewportWidth: 375,
    //   // 视口宽度（单位：vw）
    //   unitPrecision: 3,
    //   // 转换后的单位
    //   viewportUnit: 'vw',
    //   // 选择器黑名单（不转换的类名）
    //   selectorBlackList: [
    //     '.ignore',
    //     'el-',       // Element Plus 组件
    //     'vdp-',      // 第三方日期选择器等
    //     'van-'       // Vant 组件（如果需要保持原样）
    //   ],
    //   // 最小像素值
    //   minPixelValue: 1,
    //   // 允许在媒体查询中转换
    //   mediaQuery: false
    // }
  }
}