import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { colors, STATUS_STYLE, PRIORITY_STYLE } from '../theme';
import { useAuth } from '../context/AuthContext';
import { uploadResolutionPhoto } from '../api';

export default function TicketDetailScreen({ route }) {
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
        <View style={styles.card}>
          <Text style={styles.cardLabel}>Foto de resolución</Text>
          <Image
            source={{ uri: ticket.resolution_photo_url, headers: { Authorization: `Bearer ${token}` } }}
            style={[styles.photo, { marginTop: 8, marginBottom: 0 }]}
          />
        </View>
      )}

      {user?.role === 'agent' && (
        <View style={styles.card}>
          <Text style={styles.cardLabel}>
            {ticket.resolution_photo_url ? 'Reemplazar foto de resolución' : 'Foto de resolución'}
          </Text>
          {!!uploadError && <Text style={{ color: colors.danger, marginBottom: 8 }}>{uploadError}</Text>}
          <TouchableOpacity style={styles.resolutionButton} onPress={takeResolutionPhoto} disabled={uploading}>
            {uploading ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.resolutionButtonText}>
                📷 {ticket.resolution_photo_url ? 'Tomar otra foto' : 'Tomar foto de resolución'}
              </Text>
            )}
          </TouchableOpacity>
        </View>
      )}

      <View style={styles.badgeRow}>
        <View style={[styles.badge, { backgroundColor: status.bg }]}>
          <Text style={[styles.badgeText, { color: status.fg }]}>{status.label}</Text>
        </View>
        <View style={[styles.badge, { backgroundColor: priority.bg }]}>
          <Text style={[styles.badgeText, { color: priority.fg }]}>Prioridad {priority.label}</Text>
        </View>
      </View>

      <Text style={styles.title}>{ticket.title}</Text>
      {createdAt && (
        <Text style={styles.date}>
          Reportado el {createdAt.toLocaleDateString()} a las {createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </Text>
      )}

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Descripción de la falla</Text>
        <Text style={styles.cardBody}>{ticket.body}</Text>
      </View>

      <View style={styles.card}>
        <Text style={styles.cardLabel}>Folio</Text>
        <Text style={styles.cardBody}>#{ticket.id}</Text>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: colors.background },
  photo: { width: '100%', height: 220, borderRadius: 14, backgroundColor: colors.surface, marginBottom: 14 },
  photoPlaceholder: { justifyContent: 'center', alignItems: 'center', borderWidth: 1, borderColor: colors.border, borderStyle: 'dashed' },
  badgeRow: { flexDirection: 'row', gap: 8, marginBottom: 10 },
  badge: { borderRadius: 20, paddingVertical: 4, paddingHorizontal: 10, marginRight: 8 },
  badgeText: { fontSize: 12, fontWeight: '700' },
  title: { fontSize: 20, fontWeight: '700', color: colors.text },
  date: { fontSize: 12, color: colors.textMuted, marginTop: 4, marginBottom: 16 },
  card: {
    backgroundColor: colors.surface, borderRadius: 12, padding: 14, marginBottom: 12,
    shadowColor: '#000', shadowOpacity: 0.04, shadowRadius: 6, shadowOffset: { width: 0, height: 2 }, elevation: 1,
  },
  cardLabel: { fontSize: 12, color: colors.textMuted, marginBottom: 4, fontWeight: '600' },
  cardBody: { fontSize: 15, color: colors.text, lineHeight: 21 },
  resolutionButton: { backgroundColor: colors.primary, borderRadius: 10, padding: 12, marginTop: 8 },
  resolutionButtonText: { color: '#fff', textAlign: 'center', fontWeight: '600', fontSize: 14 },
});
