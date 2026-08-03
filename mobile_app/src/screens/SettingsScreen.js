import React from 'react';
import { Text, View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { colors, typography, radius } from '../theme';
import Screen from '../components/Screen';

export default function SettingsScreen({ navigation }) {
  const { logout } = useAuth();

  return (
    <Screen>
      <Text style={typography.sectionHeader}>Cuenta</Text>
      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('ChangePassword')}>
        <Ionicons name="key-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Cambiar contraseña</Text>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
      </TouchableOpacity>
      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('Profile')}>
        <Ionicons name="person-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Ver perfil</Text>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
      </TouchableOpacity>

      <Text style={[typography.sectionHeader, { marginTop: 20 }]}>Acerca de</Text>
      <View style={styles.row}>
        <Ionicons name="information-circle-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Fixu App Móvil — v1.0.0</Text>
      </View>

      <TouchableOpacity style={[styles.row, { marginTop: 20 }]} onPress={logout}>
        <Ionicons name="log-out-outline" size={20} color={colors.danger} />
        <Text style={[styles.rowText, { color: colors.danger }]}>Cerrar sesión</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.white, borderRadius: radius.md,
    padding: 14, marginTop: 10, gap: 10,
  },
  rowText: { flex: 1, fontSize: 14, fontWeight: '600', color: colors.textPrimary },
});
