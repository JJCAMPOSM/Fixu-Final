import React, { useState } from 'react';
import { Text, View, StyleSheet } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { changePassword } from '../api';
import { colors, typography } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';
import PasswordInput from '../components/PasswordInput';
import Button from '../components/Button';

const PASSWORD_RULES = [
  { key: 'length', label: 'Al menos 8 caracteres', test: (pw) => pw.length >= 8 },
  { key: 'letter', label: 'Al menos 1 letra', test: (pw) => /[a-zA-Z]/.test(pw) },
  { key: 'number', label: 'Al menos 1 número', test: (pw) => /[0-9]/.test(pw) },
];

export default function ChangePasswordScreen({ navigation }) {
  const { token } = useAuth();
  const [currentPassword, setCurrentPassword] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (!currentPassword) {
      setError('Ingresa tu contraseña actual.');
      return;
    }
    if (!PASSWORD_RULES.every((rule) => rule.test(newPassword))) {
      setError('La nueva contraseña no cumple con los requisitos.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Las contraseñas no coinciden.');
      return;
    }
    setError('');
    setSuccess('');
    setLoading(true);
    try {
      await changePassword(token, currentPassword, newPassword);
      setSuccess('Contraseña actualizada correctamente.');
      setCurrentPassword('');
      setNewPassword('');
      setConfirmPassword('');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <Card>
        <Text style={typography.label}>Contraseña actual</Text>
        <View style={{ marginTop: 4, marginBottom: 14 }}>
          <PasswordInput placeholder="••••••••" value={currentPassword} onChangeText={setCurrentPassword} />
        </View>

        <Text style={typography.label}>Nueva contraseña</Text>
        <View style={{ marginTop: 4 }}>
          <PasswordInput placeholder="Mínimo 8 caracteres" value={newPassword} onChangeText={setNewPassword} />
        </View>
        <View style={styles.rulesList}>
          {PASSWORD_RULES.map((rule) => {
            const met = rule.test(newPassword);
            return (
              <Text key={rule.key} style={[styles.ruleItem, met && styles.ruleItemMet]}>
                {met ? '✓' : '•'} {rule.label}
              </Text>
            );
          })}
        </View>

        <Text style={[typography.label, { marginTop: 14 }]}>Confirmar nueva contraseña</Text>
        <View style={{ marginTop: 4, marginBottom: 14 }}>
          <PasswordInput placeholder="Repite la nueva contraseña" value={confirmPassword} onChangeText={setConfirmPassword} />
        </View>

        {!!success && <Text style={styles.success}>{success}</Text>}
        {!!error && <Text style={styles.error}>{error}</Text>}

        <Button label="Guardar cambios" onPress={handleSubmit} loading={loading} />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  rulesList: { marginTop: 8 },
  ruleItem: { fontSize: 12, color: colors.textMuted, marginBottom: 2 },
  ruleItemMet: { color: colors.success },
  success: { color: colors.success, marginBottom: 10, marginTop: 10 },
  error: { color: colors.danger, marginBottom: 10, marginTop: 10 },
});
