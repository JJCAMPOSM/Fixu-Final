import React, { useState } from 'react';
import { Text, View, StyleSheet, TouchableOpacity } from 'react-native';
import { forgotPassword, resetPassword } from '../api';
import { colors, typography } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';
import FormField from '../components/FormField';
import Button from '../components/Button';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function ForgotPasswordScreen({ navigation }) {
  const [step, setStep] = useState('request'); // request | reset
  const [email, setEmail] = useState('');
  const [resetToken, setResetToken] = useState('');
  const [newPassword, setNewPassword] = useState('');
  const [error, setError] = useState('');
  const [info, setInfo] = useState('');
  const [loading, setLoading] = useState(false);

  const handleRequest = async () => {
    if (!EMAIL_REGEX.test(email.trim())) {
      setError('Ingresa un correo válido.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await forgotPassword(email.trim().toLowerCase());
      setInfo('Si el correo existe, se generó un enlace de recuperación (pídele el código a soporte/administrador mientras no haya envío de email configurado).');
      setStep('reset');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  const handleReset = async () => {
    if (!resetToken.trim()) {
      setError('Ingresa el código de recuperación.');
      return;
    }
    if (newPassword.length < 8) {
      setError('La nueva contraseña debe tener al menos 8 caracteres.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await resetPassword(resetToken.trim(), newPassword);
      navigation.navigate('Login');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <Text style={[typography.pageTitle, { marginBottom: 4 }]}>Recuperar contraseña</Text>
      <Text style={styles.subtitle}>
        {step === 'request'
          ? 'Ingresa tu correo para generar un código de recuperación.'
          : 'Ingresa el código que te compartió soporte y tu nueva contraseña.'}
      </Text>

      <Card>
        {step === 'request' ? (
          <>
            <FormField label="Correo" placeholder="correo@fixu.local" value={email} onChangeText={setEmail} autoCapitalize="none" keyboardType="email-address" />
            {!!info && <Text style={styles.info}>{info}</Text>}
            {!!error && <Text style={styles.error}>{error}</Text>}
            <Button label="Enviar" onPress={handleRequest} loading={loading} />
          </>
        ) : (
          <>
            {!!info && <Text style={styles.info}>{info}</Text>}
            <FormField label="Código de recuperación" placeholder="Pega aquí el código" value={resetToken} onChangeText={setResetToken} autoCapitalize="none" />
            <FormField label="Nueva contraseña" placeholder="Mínimo 8 caracteres" value={newPassword} onChangeText={setNewPassword} secureTextEntry />
            {!!error && <Text style={styles.error}>{error}</Text>}
            <Button label="Cambiar contraseña" onPress={handleReset} loading={loading} />
          </>
        )}

        <TouchableOpacity style={styles.link} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.linkText}>Volver a iniciar sesión</Text>
        </TouchableOpacity>
      </Card>
    </Screen>
  );
}

const styles = StyleSheet.create({
  subtitle: { fontSize: 13, color: colors.textSecondary, marginBottom: 20 },
  info: { color: colors.textSecondary, fontSize: 12, marginBottom: 12 },
  error: { color: colors.danger, marginBottom: 10 },
  link: { marginTop: 16, padding: 4 },
  linkText: { color: colors.accent, textAlign: 'center', fontWeight: '600', fontSize: 13 },
});
