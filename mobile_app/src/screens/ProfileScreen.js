import React from 'react';
import { Text, View, StyleSheet, TouchableOpacity } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { colors, typography, radius } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';
import Badge from '../components/Badge';

const ROLE_LABEL = { agent: 'Agente de campo', requester: 'Solicitante', admin: 'Administrador' };

export default function ProfileScreen({ navigation }) {
  const { user, logout } = useAuth();

  return (
    <Screen>
      <View style={styles.avatarWrap}>
        <View style={styles.avatar}>
          <Ionicons name="person" size={40} color={colors.white} />
        </View>
        <Text style={[typography.pageTitle, { fontSize: 20, marginTop: 10 }]}>{user?.name}</Text>
        <Badge label={ROLE_LABEL[user?.role] || user?.role} bg={colors.accentBg} fg={colors.accent} />
      </View>

      <Card style={{ marginTop: 20 }}>
        <Text style={styles.label}>Correo</Text>
        <Text style={styles.value}>{user?.email}</Text>
      </Card>

      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('ChangePassword')}>
        <Ionicons name="key-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Cambiar contraseña</Text>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
      </TouchableOpacity>

      <TouchableOpacity style={styles.row} onPress={() => navigation.navigate('Settings')}>
        <Ionicons name="settings-outline" size={20} color={colors.textPrimary} />
        <Text style={styles.rowText}>Configuración</Text>
        <Ionicons name="chevron-forward" size={18} color={colors.textMuted} />
      </TouchableOpacity>

      <TouchableOpacity style={[styles.row, { marginTop: 20 }]} onPress={logout}>
        <Ionicons name="log-out-outline" size={20} color={colors.danger} />
        <Text style={[styles.rowText, { color: colors.danger }]}>Cerrar sesión</Text>
      </TouchableOpacity>
    </Screen>
  );
}

const styles = StyleSheet.create({
  avatarWrap: { alignItems: 'center', marginBottom: 8 },
  avatar: { width: 80, height: 80, borderRadius: 40, backgroundColor: colors.accent, justifyContent: 'center', alignItems: 'center' },
  label: { fontSize: 12, color: colors.textMuted, marginBottom: 4, fontWeight: '600' },
  value: { fontSize: 15, color: colors.textPrimary },
  row: {
    flexDirection: 'row', alignItems: 'center', backgroundColor: colors.white, borderRadius: radius.md,
    padding: 14, marginTop: 10, gap: 10,
  },
  rowText: { flex: 1, fontSize: 14, fontWeight: '600', color: colors.textPrimary },
});
