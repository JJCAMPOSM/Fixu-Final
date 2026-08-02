import React, { useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors } from '../theme';

export default function PasswordInput({ value, onChangeText, placeholder, ...rest }) {
  const [visible, setVisible] = useState(false);

  return (
    <View style={styles.wrap}>
      <TextInput
        style={styles.input}
        placeholder={placeholder}
        placeholderTextColor={colors.textMuted}
        secureTextEntry={!visible}
        value={value}
        onChangeText={onChangeText}
        autoCapitalize="none"
        {...rest}
      />
      <TouchableOpacity style={styles.toggle} onPress={() => setVisible((v) => !v)}>
        <Ionicons name={visible ? 'eye-off' : 'eye'} size={20} color={colors.textMuted} />
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { position: 'relative', justifyContent: 'center' },
  input: {
    backgroundColor: colors.background, color: colors.text, borderRadius: 10, padding: 14,
    paddingRight: 44, fontSize: 16, borderWidth: 1, borderColor: colors.border,
  },
  toggle: { position: 'absolute', right: 12, padding: 4 },
});
