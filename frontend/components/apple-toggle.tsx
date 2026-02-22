import React, { useEffect, useRef } from 'react';
import { Animated, Pressable, StyleSheet, View } from 'react-native';

interface AppleToggleProps {
  value: boolean;
  onValueChange: (v: boolean) => void;
  activeColor?: string;
  inactiveColor?: string;
  size?: number;
}

export function AppleToggle({
  value,
  onValueChange,
  activeColor = '#34C759',
  inactiveColor = '#E5E5EA',
  size = 51,
}: AppleToggleProps) {
  const anim = useRef(new Animated.Value(value ? 1 : 0)).current;

  useEffect(() => {
    Animated.spring(anim, {
      toValue: value ? 1 : 0,
      useNativeDriver: false,
      friction: 8,
      tension: 60,
    }).start();
  }, [value, anim]);

  const knobSize = size * 0.52;
  const trackWidth = size;
  const trackHeight = size * 0.61;
  const padding = (trackHeight - knobSize) / 2;
  const travelDist = trackWidth - knobSize - padding * 2;

  const bgColor = anim.interpolate({
    inputRange: [0, 1],
    outputRange: [inactiveColor, activeColor],
  });

  const translateX = anim.interpolate({
    inputRange: [0, 1],
    outputRange: [padding, padding + travelDist],
  });

  const knobScale = anim.interpolate({
    inputRange: [0, 0.5, 1],
    outputRange: [1, 1.1, 1],
  });

  return (
    <Pressable onPress={() => onValueChange(!value)} hitSlop={8}>
      <Animated.View
        style={[
          styles.track,
          {
            width: trackWidth,
            height: trackHeight,
            borderRadius: trackHeight / 2,
            backgroundColor: bgColor,
          },
        ]}
      >
        <Animated.View
          style={[
            styles.knob,
            {
              width: knobSize,
              height: knobSize,
              borderRadius: knobSize / 2,
              transform: [{ translateX }, { scale: knobScale }],
            },
          ]}
        />
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  track: {
    justifyContent: 'center',
  },
  knob: {
    backgroundColor: '#FFFFFF',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 2 },
    shadowOpacity: 0.2,
    shadowRadius: 3,
    elevation: 4,
  },
});
