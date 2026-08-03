import React, { useState } from 'react';
import { View, Text, StyleSheet, Pressable } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../context/AuthContext';
import { submitFeedback } from '../api';
import { colors, typography } from '../theme';
import Screen from '../components/Screen';
import Card from '../components/Card';
import FormField from '../components/FormField';
import Button from '../components/Button';

export default function EvaluateAttentionScreen({ route, navigation }) {
  const { token } = useAuth();
  const { ticket } = route.params;
  const [rating, setRating] = useState(0);
  const [comment, setComment] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async () => {
    if (rating < 1) {
      setError('Selecciona una calificación de 1 a 5 estrellas.');
      return;
    }
    setError('');
    setLoading(true);
    try {
      await submitFeedback(token, ticket.id, rating, comment.trim());
      navigation.navigate('Tickets');
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Screen>
      <Text style={[typography.pageTitle, { fontSize: 20, marginBottom: 4 }]}>Evaluar atención</Text>
      <Text style={styles.subtitle}>#{ticket.id} · {ticket.title}</Text>

      <Card style={{ alignItems: 'center', marginTop: 20, marginBottom: 20 }}>
        <Text style={styles.question}>¿Cómo calificarías la atención recibida?</Text>
        <View style={styles.starsRow}>
          {[1, 2, 3, 4, 5].map((n) => (
            <Pressable key={n} onPress={() => setRating(n)} hitSlop={6}>
              <Ionicons
                name={n <= rating ? 'star' : 'star-outline'}
                size={32}
                color={n <= rating ? colors.warning : colors.textMuted}
                style={{ marginHorizontal: 4 }}
              />
            </Pressable>
          ))}
        </View>
      </Card>

      <FormField label="Comentarios (opcional)" placeholder="Cuéntanos más sobre tu experiencia..." multiline value={comment} onChangeText={setComment} />

      {!!error && <Text style={styles.error}>{error}</Text>}

      <Button label="Enviar evaluación" onPress={handleSubmit} loading={loading} />
    </Screen>
  );
}

const styles = StyleSheet.create({
  subtitle: { fontSize: 13, color: colors.textSecondary, marginBottom: 8 },
  question: { fontSize: 14, color: colors.textPrimary, fontWeight: '600', marginBottom: 14, textAlign: 'center' },
  starsRow: { flexDirection: 'row' },
  error: { color: colors.danger, marginBottom: 10 },
});
