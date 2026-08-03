import React, { useState } from 'react';
import { Text, StyleSheet } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { changePassword } from '../api';
import { colors } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';
import FormField from '../components/FormField';
import Button from '../components/Button';

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
    if (newPassword.length < 8) {
      setError('La nueva contraseña debe tener al menos 8 caracteres.');
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
        <FormField label="Contraseña actual" placeholder="••••••••" value={currentPassword} onChangeText={setCurrentPassword} secureTextEntry />
        <FormField label="Nueva contraseña" placeholder="Mínimo 8 caracteres" value={newPassword} onChangeText={setNewPassword} secureTextEntry />
        <FormField label="Confirmar nueva contraseña" placeholder="Repite la nueva contraseña" value={confirmPassword} onChangeText={setConfirmPassword} secureTextEntry />

        {!!success && <Text style={styles.success}>{success}</Text>}
        {!!error && <Text style={styles.error}>{error}</Text>}

        <Button label="Guardar cambios" onPress={handleSubmit} loading={loading} />
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  success: { color: colors.success, marginBottom: 10 },
  error: { color: colors.danger, marginBottom: 10 },
});
