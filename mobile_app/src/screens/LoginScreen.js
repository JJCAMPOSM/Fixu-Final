import React, { useState } from 'react';
import { View, Text, TextInput, TouchableOpacity, StyleSheet } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { colors, typography, radius } from '../theme';
import PasswordInput from '../components/PasswordInput';
import Button from '../components/Button';
import Card from '../components/Card';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function LoginScreen({ navigation }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (!EMAIL_REGEX.test(email.trim())) return 'Ingresa un correo válido.';
    if (!password) return 'Ingresa tu contraseña.';
    return null;
  };

  const handleSubmit = async () => {
    const validationError = validate();
    if (validationError) {
      setError(validationError);
      return;
    }
    setError('');
    setLoading(true);
    try {
      await login(email.trim().toLowerCase(), password);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <View style={styles.logoWrap}>
        <View style={styles.logoCircle}>
          <Text style={styles.logoEmoji}>🔧</Text>
        </View>
        <Text style={[typography.pageTitle, { fontSize: 26 }]}>FixU Campo</Text>
        <Text style={styles.subtitle}>Reporta fallas desde el sitio, con evidencia fotográfica</Text>
      </View>

      <Card>
        <Text style={styles.label}>Correo</Text>
        <TextInput
          style={styles.input}
          placeholder="correo@fixu.local"
          placeholderTextColor={colors.textMuted}
          autoCapitalize="none"
          keyboardType="email-address"
          value={email}
          onChangeText={setEmail}
        />
        <Text style={styles.label}>Contraseña</Text>
        <PasswordInput placeholder="••••••••" value={password} onChangeText={setPassword} />

        <TouchableOpacity style={styles.forgotLink} onPress={() => navigation.navigate('ForgotPassword')}>
          <Text style={styles.forgotLinkText}>¿Olvidaste tu contraseña?</Text>
        </TouchableOpacity>

        {!!error && <Text style={styles.error}>{error}</Text>}

        <View style={{ marginTop: 20 }}>
          <Button label="Iniciar sesión" onPress={handleSubmit} loading={loading} />
        </View>

        <TouchableOpacity style={styles.link} onPress={() => navigation.navigate('Register')}>
          <Text style={styles.linkText}>¿No tienes cuenta? Regístrate</Text>
        </TouchableOpacity>
      </Card>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, justifyContent: 'center', padding: 24, backgroundColor: colors.pageBg },
  logoWrap: { alignItems: 'center', marginBottom: 28 },
  logoCircle: {
    width: 64, height: 64, borderRadius: 32, backgroundColor: colors.accent,
    justifyContent: 'center', alignItems: 'center', marginBottom: 12,
  },
  logoEmoji: { fontSize: 30 },
  subtitle: { fontSize: 13, color: colors.textMuted, textAlign: 'center', marginTop: 4, paddingHorizontal: 20 },
  label: { color: colors.textSecondary, fontSize: 13, marginBottom: 6, marginTop: 10 },
  input: {
    backgroundColor: colors.pageBg, color: colors.textPrimary, borderRadius: radius.sm, padding: 14,
    fontSize: 16, borderWidth: 1, borderColor: colors.border,
  },
  forgotLink: { alignSelf: 'flex-end', marginTop: 10 },
  forgotLinkText: { color: colors.accent, fontSize: 12, fontWeight: '600' },
  error: { color: colors.danger, marginTop: 10 },
  link: { marginTop: 16, padding: 4 },
  linkText: { color: colors.accent, textAlign: 'center', fontWeight: '600', fontSize: 13 },
});
