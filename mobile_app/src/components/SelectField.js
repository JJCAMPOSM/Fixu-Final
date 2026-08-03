import React, { useState } from 'react';
import { View, Text, Pressable, StyleSheet, Modal, FlatList } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { colors, typography, radius } from '../theme';

export default function SelectField({
  label,
  placeholder = 'Selecciona una opción',
  required = false,
  options = [],
  value,
  onChange,
  labelExtractor = (item) => item,
  keyExtractor = (item) => String(item),
}) {
  const [open, setOpen] = useState(false);

  return (
    <View style={styles.wrap}>
      <Text style={typography.label}>
        {label} {required && <Text style={{ color: colors.danger }}>*</Text>}
      </Text>

      <Pressable style={styles.input} onPress={() => setOpen(true)}>
        <Text style={value != null ? styles.valueText : styles.placeholderText}>
          {value != null ? labelExtractor(value) : placeholder}
        </Text>
        <Ionicons name="chevron-down" size={16} color={colors.textMuted} />
      </Pressable>

      <Modal visible={open} transparent animationType="fade" onRequestClose={() => setOpen(false)}>
        <Pressable style={styles.backdrop} onPress={() => setOpen(false)}>
          <View style={styles.sheet}>
            <Text style={styles.sheetTitle}>{label}</Text>
            <FlatList
              data={options}
              keyExtractor={keyExtractor}
              style={{ maxHeight: 280 }}
              renderItem={({ item }) => {
                const selected = keyExtractor(item) === keyExtractor(value ?? {});
                return (
                  <Pressable
                    style={styles.option}
                    onPress={() => {
                      onChange?.(item);
                      setOpen(false);
                    }}
                  >
                    <Text style={[styles.optionText, selected && { color: colors.accent, fontWeight: '600' }]}>
                      {labelExtractor(item)}
                    </Text>
                    {selected && <Ionicons name="checkmark" size={16} color={colors.accent} />}
                  </Pressable>
                );
              }}
            />
          </View>
        </Pressable>
      </Modal>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { marginBottom: 14 },
  input: {
    marginTop: 4, height: 44, borderWidth: 1, borderColor: colors.border, borderRadius: radius.sm,
    paddingHorizontal: 12, backgroundColor: colors.white, flexDirection: 'row',
    alignItems: 'center', justifyContent: 'space-between',
  },
  valueText: { fontSize: 14, color: colors.textPrimary },
  placeholderText: { fontSize: 14, color: colors.textMuted },
  backdrop: { flex: 1, backgroundColor: 'rgba(0,0,0,0.35)', justifyContent: 'flex-end' },
  sheet: {
    backgroundColor: colors.white, borderTopLeftRadius: radius.lg, borderTopRightRadius: radius.lg,
    paddingTop: 16, paddingBottom: 24, paddingHorizontal: 16,
  },
  sheetTitle: { ...typography.sectionHeader, marginBottom: 10 },
  option: {
    flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between',
    paddingVertical: 14, borderBottomWidth: 1, borderBottomColor: colors.border,
  },
  optionText: { fontSize: 14, color: colors.textPrimary },
});
