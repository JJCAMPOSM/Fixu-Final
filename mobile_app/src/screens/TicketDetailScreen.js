import React, { useState } from 'react';
import { View, Text, Image, StyleSheet, ScrollView, TouchableOpacity } from 'react-native';
import * as ImagePicker from 'expo-image-picker';
import { Ionicons } from '@expo/vector-icons';
import { colors, radius, STATUS_STYLE, PRIORITY_STYLE } from '../theme';
import { useAuth } from '../context/AuthContext';
import { uploadResolutionPhoto, cancelTicket, updateTicketStatus, withAuthToken } from '../api';
import Badge from '../components/Badge';
import Card from '../components/Card';
import Button from '../components/Button';

const PROGRESS_STEPS = ['Recibido', 'Asignado', 'En reparación', 'Finalizado', 'Evaluar atención'];

const AGENT_STATUS_OPTIONS = [
  { value: 'in_progress', label: 'En proceso' },
  { value: 'on_hold', label: 'En espera' },
  { value: 'cancelled', label: 'Cancelado' },
  { value: 'resolved', label: 'Resuelto' },
];

function TicketProgress({ ticket }) {
  if (ticket.status === 'cancelled') {
    return <Badge label="Ticket cancelado" bg={colors.dangerBg} fg={colors.danger} />;
  }

  const assigned = ['assigned', 'in_progress', 'on_hold', 'resolved'].includes(ticket.status);
  const inRepair = ['in_progress', 'on_hold', 'resolved'].includes(ticket.status);
  const done = ticket.status === 'resolved';
  const evaluated = !!ticket.has_feedback;
  const stepDone = [true, assigned, inRepair, done, evaluated];

  return (
    <View style={styles.progressList}>
      {PROGRESS_STEPS.map((label, i) => (
        <View key={label} style={styles.progressStep}>
          <View style={styles.progressMarkerCol}>
            <View style={[styles.progressDot, stepDone[i] && styles.progressDotDone]}>
              {stepDone[i] && <Text style={styles.progressDotCheck}>✓</Text>}
            </View>
            {i < PROGRESS_STEPS.length - 1 && (
              <View style={[styles.progressLine, stepDone[i + 1] && styles.progressLineDone]} />
            )}
          </View>
          <Text style={[styles.progressLabel, stepDone[i] && styles.progressLabelDone]}>{label}</Text>
        </View>
      ))}
    </View>
  );
}

export default function TicketDetailScreen({ route, navigation }) {
  const { token, user } = useAuth();
  const [ticket, setTicket] = useState(route.params.ticket);
  const [uploading, setUploading] = useState(false);
  const [uploadError, setUploadError] = useState('');
  const [statusUpdating, setStatusUpdating] = useState(false);
  const [statusError, setStatusError] = useState('');
  const [cancelling, setCancelling] = useState(false);
  const status = STATUS_STYLE[ticket.status] || STATUS_STYLE.pending;
  const priority = PRIORITY_STYLE[ticket.priority] || PRIORITY_STYLE.medium;
  const createdAt = ticket.created_at ? new Date(ticket.created_at) : null;

  const canCancel = user?.role === 'requester' && ['pending', 'assigned'].includes(ticket.status);

  const handleCancel = async () => {
    setStatusError('');
    setCancelling(true);
    try {
      const data = await cancelTicket(token, ticket.id);
      setTicket((t) => ({ ...t, status: data.status }));
    } catch (e) {
      setStatusError(e.message);
    } finally {
      setCancelling(false);
    }
  };

  const handleStatusChange = async (newStatus) => {
    setStatusError('');
    setStatusUpdating(true);
    try {
      const data = await updateTicketStatus(token, ticket.id, newStatus);
      setTicket((t) => ({ ...t, status: data.status }));
    } catch (e) {
      setStatusError(e.message);
    } finally {
      setStatusUpdating(false);
    }
  };

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

  const canEvaluate = user?.role === 'requester' && ticket.status === 'resolved' && !ticket.has_feedback;

  return (
    <ScrollView style={styles.container} contentContainerStyle={{ padding: 20, paddingBottom: 40 }}>
      {ticket.photo_url ? (
        <Image
          source={{ uri: withAuthToken(ticket.photo_url, token) }}
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
            source={{ uri: withAuthToken(ticket.resolution_photo_url, token) }}
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

      {user?.role === 'agent' && !['cancelled', 'resolved'].includes(ticket.status) && (
        <Card style={{ marginBottom: 12 }}>
          <Text style={styles.cardLabel}>Cambiar estado</Text>
          {!!statusError && <Text style={{ color: colors.danger, marginBottom: 8 }}>{statusError}</Text>}
          <View style={{ flexDirection: 'row', flexWrap: 'wrap', gap: 8 }}>
            {AGENT_STATUS_OPTIONS.filter((o) => o.value !== ticket.status).map((o) => (
              <TouchableOpacity
                key={o.value}
                onPress={() => handleStatusChange(o.value)}
                disabled={statusUpdating}
                style={styles.statusOption}
              >
                <Text style={styles.statusOptionText}>{o.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
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

      {(ticket.building || ticket.classroom || ticket.equipment_type) && (
        <Card style={{ marginBottom: 12 }}>
          <Text style={styles.cardLabel}>Ubicación / equipo</Text>
          <Text style={styles.cardBody}>
            {[ticket.building, ticket.classroom, ticket.equipment_type].filter(Boolean).join(' · ')}
          </Text>
        </Card>
      )}

      <Card style={{ marginBottom: 12 }}>
        <Text style={styles.cardLabel}>Folio</Text>
        <Text style={styles.cardBody}>#{ticket.id}</Text>
      </Card>

      {user?.role === 'requester' && (
        <Card style={{ marginBottom: 12 }}>
          <Text style={styles.cardLabel}>Seguimiento del reporte</Text>
          <TicketProgress ticket={ticket} />
        </Card>
      )}

      {user?.role === 'requester' && ticket.has_feedback && !!ticket.rating && (
        <Card style={{ marginBottom: 12 }}>
          <Text style={styles.cardLabel}>Tu evaluación</Text>
          <View style={{ flexDirection: 'row', marginTop: 4, marginBottom: ticket.comentario ? 8 : 0 }}>
            {[1, 2, 3, 4, 5].map((n) => (
              <Ionicons
                key={n}
                name={n <= ticket.rating ? 'star' : 'star-outline'}
                size={20}
                color={n <= ticket.rating ? colors.warning : colors.textMuted}
                style={{ marginRight: 2 }}
              />
            ))}
          </View>
          {!!ticket.comentario && <Text style={styles.cardBody}>{ticket.comentario}</Text>}
        </Card>
      )}

      {canEvaluate && (
        <View style={{ marginBottom: 12 }}>
          <Button
            label="⭐ Evaluar la atención recibida"
            onPress={() => navigation.navigate('EvaluateAttention', { ticket, onSubmitted: setTicket })}
          />
        </View>
      )}

      {canCancel && (
        <Card style={{ marginTop: 8 }}>
          {!!statusError && <Text style={{ color: colors.danger, marginBottom: 8 }}>{statusError}</Text>}
          <Button label="Cancelar ticket" onPress={handleCancel} loading={cancelling} danger />
        </Card>
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
  progressList: { marginTop: 6 },
  progressStep: { flexDirection: 'row', alignItems: 'flex-start' },
  progressMarkerCol: { alignItems: 'center', width: 24 },
  progressDot: {
    width: 20, height: 20, borderRadius: 10, borderWidth: 2, borderColor: colors.border,
    backgroundColor: colors.white, justifyContent: 'center', alignItems: 'center',
  },
  progressDotDone: { backgroundColor: colors.success, borderColor: colors.success },
  progressDotCheck: { color: colors.white, fontSize: 11, fontWeight: '700' },
  progressLine: { width: 2, flex: 1, minHeight: 20, backgroundColor: colors.border },
  progressLineDone: { backgroundColor: colors.success },
  progressLabel: { fontSize: 14, color: colors.textMuted, marginLeft: 10, paddingBottom: 18 },
  progressLabelDone: { color: colors.textPrimary, fontWeight: '600' },
  statusOption: {
    borderWidth: 1, borderColor: colors.border, borderRadius: radius.sm,
    paddingVertical: 8, paddingHorizontal: 12, backgroundColor: colors.white,
  },
  statusOptionText: { fontSize: 13, fontWeight: '600', color: colors.textPrimary },
});
