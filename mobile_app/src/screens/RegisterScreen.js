import React, { useState } from 'react';
import { View, Text, TextInput, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import { useAuth } from '../context/AuthContext';
import { colors, typography, radius } from '../theme';
import PasswordInput from '../components/PasswordInput';
import Button from '../components/Button';
import Card from '../components/Card';

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

export default function RegisterScreen({ navigation }) {
  const { register } = useAuth();
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const validate = () => {
    if (name.trim().length < 2 || name.trim().length > 120) {
      return 'El nombre debe tener entre 2 y 120 caracteres.';
    }
    if (!EMAIL_REGEX.test(email.trim())) return 'Ingresa un correo válido.';
    if (password.length < 8) return 'La contraseña debe tener al menos 8 caracteres.';
    if (password !== confirmPassword) return 'Las contraseñas no coinciden.';
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
      await register(name.trim(), email.trim().toLowerCase(), password);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 24, paddingTop: 40 }}>
      <Text style={[typography.pageTitle, { textAlign: 'center' }]}>Crear cuenta</Text>
      <Text style={styles.subtitle}>Regístrate para reportar fallas desde el campo</Text>

      <Card>
        <Text style={styles.label}>Nombre completo</Text>
        <TextInput style={styles.input} placeholder="Tu nombre" placeholderTextColor={colors.textMuted} value={name} onChangeText={setName} />

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
        <PasswordInput placeholder="Mínimo 8 caracteres" value={password} onChangeText={setPassword} />

        <Text style={styles.label}>Confirmar contraseña</Text>
        <PasswordInput placeholder="Repite tu contraseña" value={confirmPassword} onChangeText={setConfirmPassword} />

        {!!error && <Text style={styles.error}>{error}</Text>}

        <View style={{ marginTop: 20 }}>
          <Button label="Crear cuenta" onPress={handleSubmit} loading={loading} />
        </View>

        <TouchableOpacity style={styles.link} onPress={() => navigation.navigate('Login')}>
          <Text style={styles.linkText}>¿Ya tienes cuenta? Inicia sesión</Text>
        </TouchableOpacity>
      </Card>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg },
  subtitle: { fontSize: 13, color: colors.textMuted, textAlign: 'center', marginTop: 4, marginBottom: 24 },
  label: { color: colors.textSecondary, fontSize: 13, marginBottom: 6, marginTop: 10 },
  input: {
    backgroundColor: colors.pageBg, color: colors.textPrimary, borderRadius: radius.sm, padding: 14,
    fontSize: 16, borderWidth: 1, borderColor: colors.border,
  },
  error: { color: colors.danger, marginTop: 10 },
  link: { marginTop: 16, padding: 4 },
  linkText: { color: colors.accent, textAlign: 'center', fontWeight: '600', fontSize: 13 },
});
