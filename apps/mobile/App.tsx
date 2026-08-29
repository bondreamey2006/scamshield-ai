import React from 'react';
import { StyleSheet, Text, View, TouchableOpacity, ScrollView } from 'react-native';

export default function MainHub({ navigation }: any) {
  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Header Banner */}
      <View style={styles.header}>
        <Text style={styles.appName}>ScamShield AI</Text>
        <Text style={styles.tagline}>Real-time Fraud & Scam Detection Engine</Text>
      </View>

      {/* Primary Scanner Grid */}
      <Text style={styles.sectionTitle}>Verification Tools</Text>

      <TouchableOpacity
        style={[styles.card, styles.primaryCard]}
        onPress={() => navigation?.navigate('qr-scan')}
      >
        <Text style={styles.cardIcon}>📷</Text>
        <View style={styles.cardTextContainer}>
          <Text style={styles.cardTitleText}>Scan QR Code / VPA</Text>
          <Text style={styles.cardSubtext}>Verify payment intent and detect spoofed VPAs</Text>
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.card}
        onPress={() => alert('Screenshot scanner configured for Hour 16 integration.')}
      >
        <Text style={styles.cardIcon}>🖼️</Text>
        <View style={styles.cardTextContainer}>
          <Text style={styles.cardTitle}>Analyze Payment Screenshot</Text>
          <Text style={styles.cardSubtext}>Forensics ELA & OCR verification</Text>
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.card}
        onPress={() => alert('URL scanner configured for Hour 16 integration.')}
      >
        <Text style={styles.cardIcon}>🌐</Text>
        <View style={styles.cardTextContainer}>
          <Text style={styles.cardTitle}>Scan Link / Domain</Text>
          <Text style={styles.cardSubtext}>Identify phishing links and malicious redirects</Text>
        </View>
      </TouchableOpacity>

      <TouchableOpacity
        style={styles.card}
        onPress={() => alert('Text scanner configured for Hour 16 integration.')}
      >
        <Text style={styles.cardIcon}>💬</Text>
        <View style={styles.cardTextContainer}>
          <Text style={styles.cardTitle}>Check SMS / Chat Text</Text>
          <Text style={styles.cardSubtext}>Detect urgency markers and scam phrases</Text>
        </View>
      </TouchableOpacity>

      {/* Quick Mock Trigger for Development */}
      <View style={styles.debugSection}>
        <Text style={styles.debugTitle}>Development Quick-Load</Text>
        <TouchableOpacity
          style={styles.debugButton}
          onPress={() =>
            navigation?.navigate('verdict', {
              result: {
                request_id: 'dev-test-001',
                scanner: 'qr',
                verdict: 'red',
                safety_score: 15,
                explanation: 'Mock Alert: This payment QR demands immediate transfer under false pretenses.',
                signals: [{ code: 'INTENT_MISMATCH', severity: 'high', message: 'User requested collect instead of pay.' }],
                recommended_actions: ['Cancel transaction immediately.', 'Do not share your PIN.'],
                provider_status: { llm: 'success', threat_lookup: 'success' },
                can_report: true,
              },
            })
          }
        >
          <Text style={styles.debugButtonText}>Test High-Risk Verdict View</Text>
        </TouchableOpacity>
      </View>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#F9FAFB' },
  content: { padding: 20, paddingBottom: 40 },
  header: { marginTop: 20, marginBottom: 24 },
  appName: { fontSize: 28, fontWeight: '800', color: '#111827' },
  tagline: { fontSize: 14, color: '#6B7280', marginTop: 4 },
  sectionTitle: { fontSize: 16, fontWeight: '700', color: '#374151', marginBottom: 12 },
  card: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 12,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#E5E7EB',
  },
  primaryCard: { borderColor: '#2563EB', backgroundColor: '#EFF6FF' },
  cardIcon: { fontSize: 28, marginRight: 14 },
  cardTextContainer: { flex: 1 },
  cardTitle: { fontSize: 15, fontWeight: '600', color: '#1F2937' },
  cardTitleText: { fontSize: 15, fontWeight: '700', color: '#1E40AF' },
  cardSubtext: { fontSize: 12, color: '#6B7280', marginTop: 2 },
  debugSection: { marginTop: 24, padding: 16, backgroundColor: '#FEF2F2', borderRadius: 12 },
  debugTitle: { fontSize: 12, fontWeight: '700', color: '#991B1B', textTransform: 'uppercase' },
  debugButton: { backgroundColor: '#DC2626', padding: 12, borderRadius: 8, marginTop: 8, alignItems: 'center' },
  debugButtonText: { color: '#FFFFFF', fontWeight: '600', fontSize: 13 },
});