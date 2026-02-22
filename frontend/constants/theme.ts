/**
 * Below are the colors that are used in the app. The colors are defined in the light and dark mode.
 * There are many other ways to style your app. For example, [Nativewind](https://www.nativewind.dev/), [Tamagui](https://tamagui.dev/), [unistyles](https://reactnativeunistyles.vercel.app), etc.
 */

import { Platform } from 'react-native';

const tintColor = '#B5374D';

export const Colors = {
  light: {
    text: '#060809',
    secondaryText: '#6B7280',
    background: '#FFFFFF',
    surface: '#F9FAFB',
    tint: tintColor,
    icon: '#9CA3AF',
    tabIconDefault: '#D1D5DB',
    tabIconSelected: tintColor,
    border: '#E7E8E8',
    cardShadow: 'rgba(6, 8, 9, 0.06)',
    headerBg: '#FFFFFF',
  },
  dark: {
    text: '#E7E8E8',
    secondaryText: '#9CA3AF',
    background: '#0F1212',
    surface: '#1A1D1D',
    tint: tintColor,
    icon: '#6B7280',
    tabIconDefault: '#4B5563',
    tabIconSelected: tintColor,
    border: '#2A2D2D',
    cardShadow: 'rgba(0, 0, 0, 0.4)',
    headerBg: '#0F1212',
  },
};

export const Fonts = Platform.select({
  ios: {
    /** iOS `UIFontDescriptorSystemDesignDefault` */
    sans: 'system-ui',
    /** iOS `UIFontDescriptorSystemDesignSerif` */
    serif: 'ui-serif',
    /** iOS `UIFontDescriptorSystemDesignRounded` */
    rounded: 'ui-rounded',
    /** iOS `UIFontDescriptorSystemDesignMonospaced` */
    mono: 'ui-monospace',
  },
  default: {
    sans: 'normal',
    serif: 'serif',
    rounded: 'normal',
    mono: 'monospace',
  },
  web: {
    sans: "system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif",
    serif: "Georgia, 'Times New Roman', serif",
    rounded: "'SF Pro Rounded', 'Hiragino Maru Gothic ProN', Meiryo, 'MS PGothic', sans-serif",
    mono: "SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', 'Courier New', monospace",
  },
});
