import React from 'react';
import { View, Text, StyleSheet } from 'react-native';
import { typography, radius } from '../theme';

export default function Badge({ label, bg, fg }) {
  return (
    <View style={[styles.badge, { backgroundColor: bg }]}>
      <Text style={[typography.badge, { color: fg }]}>{label}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  badge: { paddingHorizontal: 10, paddingVertical: 3, borderRadius: radius.sm, alignSelf: 'flex-start' },
});
