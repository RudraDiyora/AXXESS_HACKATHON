import React, { useState } from 'react';
import {
  StyleSheet,
  View,
  ScrollView,
  Pressable,
  TextInput,
  Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ThemedText } from '@/components/themed-text';
import { AppleToggle } from '@/components/apple-toggle';
import { useColorScheme } from '@/hooks/use-color-scheme';
import { useTheme } from '@/contexts/theme-context';
import { useAppData } from '@/contexts/data-context';
import { Colors } from '@/constants/theme';

export default function ProfilePage() {
  const router = useRouter();
  const scheme = useColorScheme() ?? 'light';
  const colors = Colors[scheme];
  const insets = useSafeAreaInsets();
  const { isDark, toggleDarkMode } = useTheme();
  const { patient, caregiver, setCaregiver } = useAppData();

  // Settings state
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [shareWithCaregiver, setShareWithCaregiver] = useState(true);

  // Caregiver edit state
  const [editing, setEditing] = useState(false);
  const [editName, setEditName] = useState(caregiver?.name ?? '');
  const [editRelationship, setEditRelationship] = useState(caregiver?.relationship ?? '');
  const [editPhone, setEditPhone] = useState(caregiver?.phone ?? '');
  const [editEmail, setEditEmail] = useState(caregiver?.email ?? '');

  const startEdit = () => {
    setEditName(caregiver?.name ?? '');
    setEditRelationship(caregiver?.relationship ?? '');
    setEditPhone(caregiver?.phone ?? '');
    setEditEmail(caregiver?.email ?? '');
    setEditing(true);
  };

  const saveCaregiver = () => {
    if (!editName.trim()) {
      Alert.alert('Name required', 'Please enter a name for the caregiver.');
      return;
    }
    setCaregiver({
      name: editName.trim(),
      relationship: editRelationship.trim(),
      phone: editPhone.trim(),
      email: editEmail.trim(),
    });
    setEditing(false);
  };

  const removeCaregiver = () => {
    Alert.alert('Remove Caregiver', 'Are you sure you want to remove this caregiver?', [
      { text: 'Cancel', style: 'cancel' },
      {
        text: 'Remove',
        style: 'destructive',
        onPress: () => {
          setCaregiver(null);
          setEditing(false);
        },
      },
    ]);
  };

  return (
    <View style={[styles.screen, { backgroundColor: colors.background }]}>
      <View style={[styles.header, { paddingTop: insets.top + 8, backgroundColor: colors.headerBg, borderBottomColor: colors.border }]}>
        <View style={styles.headerRow}>
          <Pressable onPress={() => router.back()} style={[styles.backBtn, { backgroundColor: colors.tint + '15' }]} hitSlop={12}>
            <Ionicons name="chevron-back" size={20} color={colors.tint} />
          </Pressable>
          <ThemedText style={[styles.pageTitle, { color: colors.text }]}>My Profile</ThemedText>
        </View>
      </View>

      <ScrollView style={styles.scroll} contentContainerStyle={styles.content} showsVerticalScrollIndicator={false}>
        {/* User Info */}
        <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={styles.avatarSection}>
            <View style={[styles.avatarLarge, { backgroundColor: colors.tint + '15' }]}>
              <Ionicons name="person" size={36} color={colors.tint} />
            </View>
            <View style={{ flex: 1 }}>
              <ThemedText style={[styles.userName, { color: colors.text }]}>{patient.name}</ThemedText>
              <ThemedText style={[styles.userDetail, { color: colors.secondaryText }]}>Age: {patient.age}</ThemedText>
              <ThemedText style={[styles.userDetail, { color: colors.secondaryText }]}>{patient.phone}</ThemedText>
            </View>
          </View>
        </View>

        {/* ── Settings ── */}
        <View style={styles.sectionHeader}>
          <Ionicons name="settings-outline" size={20} color={colors.tint} />
          <ThemedText style={[styles.sectionTitle, { color: colors.text }]}>Settings</ThemedText>
        </View>

        <View style={[styles.settingsGroup, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          {/* Dark Mode */}
          <View style={[styles.settingRow, { borderBottomColor: colors.border }]}>
            <View style={[styles.settingIcon, { backgroundColor: '#8B5CF615' }]}>
              <Ionicons name={isDark ? 'moon' : 'sunny'} size={18} color={isDark ? '#8B5CF6' : '#F59E0B'} />
            </View>
            <View style={{ flex: 1 }}>
              <ThemedText style={[styles.settingLabel, { color: colors.text }]}>Dark Mode</ThemedText>
              <ThemedText style={[styles.settingDesc, { color: colors.secondaryText }]}>
                {isDark ? 'On' : 'Off'}
              </ThemedText>
            </View>
            <AppleToggle
              value={isDark}
              onValueChange={toggleDarkMode}
              activeColor={colors.tint}
              inactiveColor={colors.border}
            />
          </View>

          {/* Notifications */}
          <View style={[styles.settingRow, { borderBottomColor: colors.border }]}>
            <View style={[styles.settingIcon, { backgroundColor: '#F59E0B15' }]}>
              <Ionicons name="notifications" size={18} color="#F59E0B" />
            </View>
            <View style={{ flex: 1 }}>
              <ThemedText style={[styles.settingLabel, { color: colors.text }]}>Reminders</ThemedText>
              <ThemedText style={[styles.settingDesc, { color: colors.secondaryText }]}>Appointment reminders</ThemedText>
            </View>
            <AppleToggle
              value={notificationsEnabled}
              onValueChange={setNotificationsEnabled}
              activeColor={colors.tint}
              inactiveColor={colors.border}
            />
          </View>

          {/* Share */}
          <View style={styles.settingRow}>
            <View style={[styles.settingIcon, { backgroundColor: '#10B98115' }]}>
              <Ionicons name="share-social" size={18} color="#10B981" />
            </View>
            <View style={{ flex: 1 }}>
              <ThemedText style={[styles.settingLabel, { color: colors.text }]}>Share with Caregiver</ThemedText>
              <ThemedText style={[styles.settingDesc, { color: colors.secondaryText }]}>Auto-share visit summaries</ThemedText>
            </View>
            <AppleToggle
              value={shareWithCaregiver}
              onValueChange={setShareWithCaregiver}
              activeColor={colors.tint}
              inactiveColor={colors.border}
            />
          </View>
        </View>

        {/* ── Caregiver / Family Member ── */}
        <View style={styles.sectionHeader}>
          <Ionicons name="people" size={20} color={colors.tint} />
          <ThemedText style={[styles.sectionTitle, { color: colors.text }]}>
            Caregiver / Family Member
          </ThemedText>
        </View>
        <ThemedText style={[styles.sectionDesc, { color: colors.secondaryText }]}>
          Add someone who helps manage your health. They'll be able to view your visit summaries and care plan.
        </ThemedText>

        {editing ? (
          <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <ThemedText style={[styles.fieldLabel, { color: colors.secondaryText }]}>Name *</ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, backgroundColor: colors.background, borderColor: colors.border }]}
              value={editName}
              onChangeText={setEditName}
              placeholder="Full name"
              placeholderTextColor={colors.icon}
            />

            <ThemedText style={[styles.fieldLabel, { color: colors.secondaryText }]}>Relationship</ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, backgroundColor: colors.background, borderColor: colors.border }]}
              value={editRelationship}
              onChangeText={setEditRelationship}
              placeholder="e.g. Daughter, Son, Spouse"
              placeholderTextColor={colors.icon}
            />

            <ThemedText style={[styles.fieldLabel, { color: colors.secondaryText }]}>Phone</ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, backgroundColor: colors.background, borderColor: colors.border }]}
              value={editPhone}
              onChangeText={setEditPhone}
              placeholder="(555) 000-0000"
              placeholderTextColor={colors.icon}
              keyboardType="phone-pad"
            />

            <ThemedText style={[styles.fieldLabel, { color: colors.secondaryText }]}>Email</ThemedText>
            <TextInput
              style={[styles.input, { color: colors.text, backgroundColor: colors.background, borderColor: colors.border }]}
              value={editEmail}
              onChangeText={setEditEmail}
              placeholder="email@example.com"
              placeholderTextColor={colors.icon}
              keyboardType="email-address"
              autoCapitalize="none"
            />

            <View style={styles.btnRow}>
              <Pressable
                onPress={() => setEditing(false)}
                style={[styles.btn, styles.cancelBtn, { borderColor: colors.border }]}
              >
                <ThemedText style={[styles.btnText, { color: colors.secondaryText }]}>Cancel</ThemedText>
              </Pressable>
              <Pressable onPress={saveCaregiver} style={[styles.btn, { backgroundColor: colors.tint }]}>
                <ThemedText style={[styles.btnText, { color: '#fff' }]}>Save</ThemedText>
              </Pressable>
            </View>
          </View>
        ) : caregiver ? (
          <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
            <View style={styles.caregiverHeader}>
              <View style={[styles.caregiverAvatar, { backgroundColor: '#8B5CF615' }]}>
                <Ionicons name="person" size={24} color="#8B5CF6" />
              </View>
              <View style={{ flex: 1 }}>
                <ThemedText style={[styles.caregiverName, { color: colors.text }]}>{caregiver.name}</ThemedText>
                <ThemedText style={[styles.caregiverRel, { color: colors.secondaryText }]}>{caregiver.relationship}</ThemedText>
              </View>
            </View>

            {caregiver.phone ? (
              <View style={styles.infoRow}>
                <Ionicons name="call-outline" size={16} color={colors.secondaryText} />
                <ThemedText style={[styles.infoText, { color: colors.text }]}>{caregiver.phone}</ThemedText>
              </View>
            ) : null}
            {caregiver.email ? (
              <View style={styles.infoRow}>
                <Ionicons name="mail-outline" size={16} color={colors.secondaryText} />
                <ThemedText style={[styles.infoText, { color: colors.text }]}>{caregiver.email}</ThemedText>
              </View>
            ) : null}

            <View style={[styles.btnRow, { marginTop: 16 }]}>
              <Pressable onPress={startEdit} style={[styles.btn, styles.cancelBtn, { borderColor: colors.border }]}>
                <Ionicons name="create-outline" size={16} color={colors.tint} />
                <ThemedText style={[styles.btnText, { color: colors.tint }]}>Edit</ThemedText>
              </Pressable>
              <Pressable onPress={removeCaregiver} style={[styles.btn, styles.cancelBtn, { borderColor: '#EF4444' }]}>
                <Ionicons name="trash-outline" size={16} color="#EF4444" />
                <ThemedText style={[styles.btnText, { color: '#EF4444' }]}>Remove</ThemedText>
              </Pressable>
            </View>
          </View>
        ) : (
          <Pressable
            onPress={startEdit}
            style={[styles.addCard, { borderColor: colors.tint, backgroundColor: colors.tint + '08' }]}
          >
            <Ionicons name="add-circle-outline" size={24} color={colors.tint} />
            <ThemedText style={[styles.addText, { color: colors.tint }]}>Add Caregiver</ThemedText>
          </Pressable>
        )}

        {/* ── Family Doctor ── */}
        <View style={styles.sectionHeader}>
          <Ionicons name="medkit" size={20} color={colors.tint} />
          <ThemedText style={[styles.sectionTitle, { color: colors.text }]}>Family Doctor</ThemedText>
        </View>

        <View style={[styles.card, { backgroundColor: colors.surface, borderColor: colors.border }]}>
          <View style={styles.caregiverHeader}>
            <View style={[styles.caregiverAvatar, { backgroundColor: colors.tint + '15' }]}>
              <Ionicons name="person" size={24} color={colors.tint} />
            </View>
            <View style={{ flex: 1 }}>
              <ThemedText style={[styles.caregiverName, { color: colors.text }]}>Dr. Sarah Chen</ThemedText>
              <ThemedText style={[styles.caregiverRel, { color: colors.secondaryText }]}>Family Medicine</ThemedText>
            </View>
          </View>
          <View style={styles.infoRow}>
            <Ionicons name="call-outline" size={16} color={colors.secondaryText} />
            <ThemedText style={[styles.infoText, { color: colors.text }]}>(555) 321-7890</ThemedText>
          </View>
          <View style={styles.infoRow}>
            <Ionicons name="location-outline" size={16} color={colors.secondaryText} />
            <ThemedText style={[styles.infoText, { color: colors.text }]}>Riverside Family Clinic</ThemedText>
          </View>
          <View style={styles.infoRow}>
            <Ionicons name="mail-outline" size={16} color={colors.secondaryText} />
            <ThemedText style={[styles.infoText, { color: colors.text }]}>dr.chen@riverside.med</ThemedText>
          </View>
        </View>

        {/* About */}
        <View style={[styles.aboutRow, { borderTopColor: colors.border }]}>
          <Ionicons name="information-circle-outline" size={18} color={colors.secondaryText} />
          <ThemedText style={[styles.aboutText, { color: colors.secondaryText }]}>MedScribe v1.0.0</ThemedText>
        </View>

        <View style={{ height: 40 }} />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  header: { paddingHorizontal: 20, paddingBottom: 16, borderBottomWidth: 1 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 12 },
  backBtn: { width: 36, height: 36, borderRadius: 18, alignItems: 'center', justifyContent: 'center' },
  pageTitle: { fontSize: 26, fontWeight: '800' },
  scroll: { flex: 1 },
  content: { padding: 20 },

  /* User info */
  card: { borderRadius: 14, padding: 18, borderWidth: 1, marginBottom: 16 },
  avatarSection: { flexDirection: 'row', alignItems: 'center', gap: 16 },
  avatarLarge: { width: 72, height: 72, borderRadius: 36, alignItems: 'center', justifyContent: 'center' },
  userName: { fontSize: 22, fontWeight: '800' },
  userDetail: { fontSize: 15, marginTop: 4 },

  /* Section */
  sectionHeader: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8, marginBottom: 6 },
  sectionTitle: { fontSize: 18, fontWeight: '700' },
  sectionDesc: { fontSize: 14, lineHeight: 22, marginBottom: 14 },

  /* Settings */
  settingsGroup: { borderRadius: 14, borderWidth: 1, overflow: 'hidden', marginBottom: 20 },
  settingRow: { flexDirection: 'row', alignItems: 'center', gap: 14, paddingHorizontal: 16, paddingVertical: 14, borderBottomWidth: StyleSheet.hairlineWidth },
  settingIcon: { width: 34, height: 34, borderRadius: 8, alignItems: 'center', justifyContent: 'center' },
  settingLabel: { fontSize: 16, fontWeight: '600' },
  settingDesc: { fontSize: 13, marginTop: 2 },

  /* Caregiver display */
  caregiverHeader: { flexDirection: 'row', alignItems: 'center', gap: 14, marginBottom: 12 },
  caregiverAvatar: { width: 48, height: 48, borderRadius: 24, alignItems: 'center', justifyContent: 'center' },
  caregiverName: { fontSize: 18, fontWeight: '700' },
  caregiverRel: { fontSize: 14, marginTop: 2 },
  infoRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 8 },
  infoText: { fontSize: 15 },

  /* Form */
  fieldLabel: { fontSize: 13, fontWeight: '600', textTransform: 'uppercase', letterSpacing: 0.5, marginTop: 14, marginBottom: 6 },
  input: { borderWidth: 1, borderRadius: 10, paddingHorizontal: 14, paddingVertical: 12, fontSize: 16 },
  btnRow: { flexDirection: 'row', gap: 10, marginTop: 18 },
  btn: { flex: 1, flexDirection: 'row', alignItems: 'center', justifyContent: 'center', gap: 6, paddingVertical: 12, borderRadius: 10 },
  cancelBtn: { borderWidth: 1 },
  btnText: { fontSize: 15, fontWeight: '700' },

  /* Add button */
  addCard: { borderWidth: 2, borderStyle: 'dashed', borderRadius: 14, padding: 24, alignItems: 'center', justifyContent: 'center', gap: 8 },
  addText: { fontSize: 16, fontWeight: '700' },

  /* About */
  aboutRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginTop: 20, paddingTop: 16, borderTopWidth: 1 },
  aboutText: { fontSize: 14, fontWeight: '500' },
});
