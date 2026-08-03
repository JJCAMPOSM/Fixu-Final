import React from 'react';
import { Pressable, Text, StyleSheet, ActivityIndicator } from 'react-native';
import { colors, radius } from '../theme';

export default function Button({ label, onPress, variant = 'primary', danger = false, loading = false, disabled = false }) {
  const isPrimary = variant === 'primary';

  return (
    <Pressable
      onPress={onPress}
      disabled={disabled || loading}
      style={[
        styles.base,
        isPrimary
          ? { backgroundColor: danger ? colors.danger : colors.accent }
          : { backgroundColor: colors.white, borderWidth: 1, borderColor: colors.border },
        (disabled || loading) && { opacity: 0.6 },
      ]}
    >
      {loading ? (
        <ActivityIndicator color={isPrimary ? colors.white : colors.accent} />
      ) : (
        <Text style={[styles.label, { color: isPrimary ? colors.white : danger ? colors.danger : colors.textPrimary }]}>
          {label}
        </Text>
      )}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  base: { height: 44, borderRadius: radius.sm, alignItems: 'center', justifyContent: 'center', width: '100%' },
  label: { fontSize: 14, fontWeight: '600' },
});
