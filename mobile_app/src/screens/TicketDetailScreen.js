import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { colors, radius, STATUS_STYLE, PRIORITY_STYLE } from '../theme';
import { useAuth } from '../context/AuthContext';
import { uploadResolutionPhoto } from '../api';
import Badge from '../components/Badge';
import Card from '../components/Card';
import Button from '../components/Button';

export default function TicketDetailScreen({ route, navigation }) {
  const { token, user } = useAuth();
  const [ticket, setTicket] = useState(route.params.ticket);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const status = STATUS_STYLE[ticket.status] || STATUS_STYLE.open;
  const priority = PRIORITY_STYLE[ticket.priority] || PRIORITY_STYLE.medium;
  const createdAt = ticket.created_at ? new Date(ticket.created_at) : null;

  const takeResolutionPhoto = async () => {
    setUploadError('');
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      setUploadError('Se necesita permiso de cámara para capturar la evidencia de resolución.');
      return;
    }

    const result = await ImagePicker.launchCameraAsync({ base64: true, quality: 0.5 });
    if (result.canceled || !result.assets?.[0]) return;

    setUploading(true);
    try {
      const asset = result.assets[0];
      const photo_base64 = `data:image/jpeg;base64,${asset.base64}`;
      const data = await uploadResolutionPhoto(token, ticket.id, photo_base64);
      setTicket((t) => ({ ...t, resolution_photo_url: data.resolution_photo_url }));
    } catch (e) {
      setUploadError(e.message);
    } finally {
      setUploading(false);
    }
  };

  const canEvaluate = user?.role === 'requester' && ticket.status === 'closed' && !ticket.has_feedback;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20, paddingBottom: 40 }}>
      {ticket.photo_url ? (
        <Image
          source={{ uri: ticket.photo_url, headers: { Authorization: `Bearer ${token}` } }}
          style={styles.photo}
        />
      ) : (
        <View style={[styles.photo, styles.photoPlaceholder]}>
          <Text style={{ color: colors.textMuted }}>Sin evidencia fotográfica</Text>
        </View>
      )}

      {ticket.resolution_photo_url && (
        <Card style={{ marginBottom: 12 }}>
          <Text style={styles.cardLabel}>Foto de resolución</Text>
          <Image
            source={{ uri: ticket.resolution_photo_url, headers: { Authorization: `Bearer ${token}` } }}
            style={[styles.photo, { marginTop: 8, marginBottom: 0 }]}
          />
        </Card>
      )}

      {user?.role === 'agent' && (
        <Card style={{ marginBottom: 12 }}>
          <Text style={styles.cardLabel}>
            {ticket.resolution_photo_url ? 'Reemplazar foto de resolución' : 'Foto de resolución'}
          </Text>
          {!!uploadError && <Text style={{ color: colors.danger, marginBottom: 8 }}>{uploadError}</Text>}
          <Button
            label={`📷 ${ticket.resolution_photo_url ? 'Tomar otra foto' : 'Tomar foto de resolución'}`}
            onPress={takeResolutionPhoto}
            loading={uploading}
          />
        </Card>
      )}

      <View style={styles.badgeRow}>
        <Badge label={status.label} bg={status.bg} fg={status.fg} />
        <Badge label={`Prioridad ${priority.label}`} bg={priority.bg} fg={priority.fg} />
      </View>

      <Text style={styles.title}>{ticket.title}</Text>
      {createdAt && (
        <Text style={styles.date}>
          Reportado el {createdAt.toLocaleDateString()} a las {createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      )}

      <Card style={{ marginBottom: 12 }}>
        <Text style={styles.cardLabel}>Descripción de la falla</Text>
        <Text style={styles.cardBody}>{ticket.body}</Text>
      </Card>

      <Card style={{ marginBottom: 12 }}>
        <Text style={styles.cardLabel}>Folio</Text>
        <Text style={styles.cardBody}>#{ticket.id}</Text>
      </Card>

      {canEvaluate && (
        <TouchableOpacity style={styles.evaluateLink} onPress={() => navigation.navigate('EvaluateAttention', { ticket })}>
          <Text style={styles.evaluateLinkText}>⭐ Evaluar la atención recibida</Text>
        </TouchableOpacity>
      )}
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.pageBg },
  photo: { width: '100%', height: 220, borderRadius: radius.lg, backgroundColor: colors.white, marginBottom: 14 },
  photoPlaceholder: { justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: colors.border, borderStyle: 'dashed' },
  badgeRow: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  title: { fontSize: 20, fontWeight: '700', color: colors.textPrimary },
  date: { fontSize: 12, color: colors.textMuted, marginTop: 4, marginBottom: 16 },
  cardLabel: { fontSize: 12, color: colors.textMuted, marginBottom: 4, fontWeight: '600' },
  cardBody: { fontSize: 15, color: colors.textPrimary, lineHeight: 21 },
  evaluateLink: { padding: 14, alignItems: 'center' },
  evaluateLinkText: { color: colors.accent, fontWeight: '700', fontSize: 14 },
});
