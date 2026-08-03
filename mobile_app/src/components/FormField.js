import React from 'react';
import { View, Text, TextInput, StyleSheet } from 'react-native';
import { colors, typography, radius } from '../theme';

export default function FormField({
  label,
  placeholder,
  required = false,
  secureTextEntry = false,
  multiline = false,
  value,
  onChangeText,
  error,
  ...rest
}) {
  return (
    <View style={styles.wrap}>
      <Text style={typography.label}>
        {label} {required && <Text style={{ color: colors.danger }}>*</Text>}
      </Text>
      <TextInput
        placeholder={placeholder}
        placeholderTextColor={colors.textMuted}
        secureTextEntry={secureTextEntry}
        multiline={multiline}
        value={value}
        onChangeText={onChangeText}
        style={[
          styles.input,
          multiline && { height: 80, textAlignVertical: 'top', paddingTop: 10 },
          error && { borderColor: colors.danger },
        ]}
        {...rest}
      />
      {!!error && <Text style={styles.error}>{error}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { marginBottom: 14 },
  input: {
    marginTop: 4,
    height: 44,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: 12,
    fontSize: 14,
    color: colors.textPrimary,
    backgroundColor: colors.white,
  },
  error: { color: colors.danger, fontSize: 12, marginTop: 4 },
});
