const API_BASE = '/api/v1';

class ApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = 'ApiError';
  }
}

async function fetchApi<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    credentials: 'include',
  });

  if (!response.ok) {
    const data = await response.json().catch(() => ({ detail: 'Request failed' }));
    throw new ApiError(response.status, data.detail || 'Request failed');
  }

  return response.json();
}

export const api = {
  auth: {
    login: () => fetchApi('/auth/discord/login'),
    logout: () => fetchApi('/auth/logout', { method: 'POST' }),
    me: () => fetchApi<{ user_id: string; role: string; permissions: string[] }>('/auth/me'),
  },

  dashboard: {
    summary: () => fetchApi('/dashboard/summary'),
    health: () => fetchApi('/dashboard/health'),
    live: () => fetchApi('/dashboard/live'),
  },

  giftCodes: {
    list: (params?: { status?: string; limit?: number; offset?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.status) searchParams.set('status', params.status);
      if (params?.limit) searchParams.set('limit', String(params.limit));
      if (params?.offset) searchParams.set('offset', String(params.offset));
      return fetchApi(`/gift-codes?${searchParams}`);
    },
    redeem: (code: string) => fetchApi('/gift-codes/redeem', {
      method: 'POST',
      body: JSON.stringify({ code }),
    }),
    status: (codeHash: string) => fetchApi(`/gift-codes/${codeHash}/status`),
    queue: () => fetchApi('/gift-codes/queue'),
    stats: () => fetchApi('/gift-codes/stats'),
  },

  players: {
    list: (params?: { search?: string; status?: string; limit?: number; offset?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.search) searchParams.set('search', params.search);
      if (params?.status) searchParams.set('status', params.status);
      if (params?.limit) searchParams.set('limit', String(params.limit));
      if (params?.offset) searchParams.set('offset', String(params.offset));
      return fetchApi(`/players?${searchParams}`);
    },
    stats: () => fetchApi('/players/stats'),
    disable: (playerId: string) => fetchApi(`/players/${playerId}/disable`, { method: 'POST' }),
    enable: (playerId: string) => fetchApi(`/players/${playerId}/enable`, { method: 'POST' }),
  },

  playerPanel: {
    status: () => fetchApi('/player-panel/status'),
    refresh: () => fetchApi('/player-panel/refresh', { method: 'POST' }),
    language: (lang: string) => fetchApi('/player-panel/language', {
      method: 'POST',
      body: JSON.stringify({ language: lang }),
    }),
  },

  alliances: {
    list: () => fetchApi('/alliances'),
    create: (name: string, tag: string) => fetchApi('/alliances', {
      method: 'POST',
      body: JSON.stringify({ name, tag }),
    }),
    update: (id: number, data: { name?: string; tag?: string }) => fetchApi(`/alliances/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    disable: (id: number) => fetchApi(`/alliances/${id}/disable`, { method: 'POST' }),
    members: (id: number) => fetchApi(`/alliances/${id}/members`),
    assignMember: (playerId: number, allianceId: number) => fetchApi('/alliances/member/assign', {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId, alliance_id: allianceId }),
    }),
    removeMember: (playerId: number, allianceId: number) => fetchApi('/alliances/member/remove', {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId, alliance_id: allianceId }),
    }),
    rankMember: (playerId: number, rank: string) => fetchApi('/alliances/member/rank', {
      method: 'POST',
      body: JSON.stringify({ player_id: playerId, rank }),
    }),
    stats: () => fetchApi('/alliances/stats'),
    audit: () => fetchApi('/alliances/audit'),
  },

  allianceApi: {
    health: () => fetchApi('/alliance-api/health'),
    sync: () => fetchApi('/alliance-api/sync', { method: 'POST' }),
    syncRuns: (limit?: number) => fetchApi(`/alliance-api/sync-runs?limit=${limit || 20}`),
    rankHistory: (limit?: number) => fetchApi(`/alliance-api/rank-history?limit=${limit || 50}`),
    memberHistory: (limit?: number) => fetchApi(`/alliance-api/member-history?limit=${limit || 50}`),
  },

  reminders: {
    list: (params?: { status?: string; limit?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.status) searchParams.set('status', params.status);
      if (params?.limit) searchParams.set('limit', String(params.limit));
      return fetchApi(`/reminders?${searchParams}`);
    },
    createBear: (eventName: string, eventTime: string, offsets?: number[]) => fetchApi('/reminders/bear', {
      method: 'POST',
      body: JSON.stringify({ event_name: eventName, event_time: eventTime, offsets }),
    }),
    createEvent: (eventName: string, eventTime: string, offsets?: number[], timeMode?: string) => fetchApi('/reminders/event', {
      method: 'POST',
      body: JSON.stringify({ event_name: eventName, event_time: eventTime, offsets, time_mode: timeMode }),
    }),
    createCustom: (name: string, message: string, schedule: string, timeMode?: string) => fetchApi('/reminders/custom', {
      method: 'POST',
      body: JSON.stringify({ name, message, schedule, time_mode: timeMode }),
    }),
    update: (id: number, data: { event_name?: string; event_time?: string; offsets?: number[] }) => fetchApi(`/reminders/${id}`, {
      method: 'PATCH',
      body: JSON.stringify(data),
    }),
    disable: (id: number) => fetchApi(`/reminders/${id}/disable`, { method: 'POST' }),
    test: (id: number) => fetchApi(`/reminders/${id}/test`, { method: 'POST' }),
    deliveries: (limit?: number) => fetchApi(`/reminders/deliveries?limit=${limit || 50}`),
    timeSettings: () => fetchApi('/reminders/time-settings'),
    updateTimeSettings: (data: { game_timezone?: string; real_timezone?: string; display_timezone?: string; default_time_mode?: string }) =>
      fetchApi('/reminders/time-settings', { method: 'PATCH', body: JSON.stringify(data) }),
  },

  content: {
    pages: () => fetchApi('/content/pages'),
    get: (pageKey: string, language?: string) => fetchApi(`/content/${pageKey}?language=${language || 'ar'}`),
    update: (pageKey: string, blockKey: string, value: string, language?: string) => fetchApi(`/content/${pageKey}/${blockKey}`, {
      method: 'PATCH',
      body: JSON.stringify({ value, language }),
    }),
    reset: (pageKey: string, blockKey: string) => fetchApi(`/content/${pageKey}/${blockKey}/reset`, { method: 'POST' }),
    history: (pageKey?: string) => fetchApi(`/content/history${pageKey ? `?page_key=${pageKey}` : ''}`),
  },

  admins: {
    list: () => fetchApi('/admins'),
    add: (userId: string) => fetchApi('/admins', { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
    updatePermissions: (userId: string, permissions: string[]) => fetchApi(`/admins/${userId}/permissions`, {
      method: 'PATCH',
      body: JSON.stringify({ permissions }),
    }),
    remove: (userId: string) => fetchApi(`/admins/${userId}`, { method: 'DELETE' }),
    supervisors: () => fetchApi('/admins/supervisors'),
    addSupervisor: (userId: string) => fetchApi('/admins/supervisors', { method: 'POST', body: JSON.stringify({ user_id: userId }) }),
    updateSupervisorPermissions: (userId: string, permissions: string[]) => fetchApi(`/admins/supervisors/${userId}/permissions`, {
      method: 'PATCH',
      body: JSON.stringify({ permissions }),
    }),
    removeSupervisor: (userId: string) => fetchApi(`/admins/supervisors/${userId}`, { method: 'DELETE' }),
  },

  security: {
    incidents: (limit?: number) => fetchApi(`/security/incidents?limit=${limit || 50}`),
    auditLogs: (limit?: number) => fetchApi(`/security/audit-logs?limit=${limit || 50}`),
    scan: () => fetchApi('/security/scan', { method: 'POST' }),
    integrityCheck: () => fetchApi('/security/integrity-check', { method: 'POST' }),
  },

  system: {
    status: () => fetchApi('/system/status'),
    diagnostics: () => fetchApi('/system/diagnostics'),
    autopilot: () => fetchApi('/system/autopilot'),
    watchdog: () => fetchApi('/system/watchdog'),
    predict: () => fetchApi('/system/predict'),
  },

  backups: {
    list: (limit?: number) => fetchApi(`/backups?limit=${limit || 20}`),
    create: () => fetchApi('/backups/create', { method: 'POST' }),
    rollback: (backupId: string) => fetchApi(`/backups/${backupId}/rollback`, { method: 'POST' }),
  },

  updates: {
    check: () => fetchApi('/updates/check'),
    plan: () => fetchApi('/updates/plan'),
    apply: () => fetchApi('/updates/apply', { method: 'POST' }),
  },

  audit: {
    logs: (params?: { actor_id?: string; action?: string; result?: string; risk_level?: string; limit?: number; offset?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.actor_id) searchParams.set('actor_id', params.actor_id);
      if (params?.action) searchParams.set('action', params.action);
      if (params?.result) searchParams.set('result', params.result);
      if (params?.risk_level) searchParams.set('risk_level', params.risk_level);
      if (params?.limit) searchParams.set('limit', String(params.limit));
      if (params?.offset) searchParams.set('offset', String(params.offset));
      return fetchApi(`/audit/logs?${searchParams}`);
    },
    web: (params?: { actor_id?: string; action?: string; limit?: number; offset?: number }) => {
      const searchParams = new URLSearchParams();
      if (params?.actor_id) searchParams.set('actor_id', params.actor_id);
      if (params?.action) searchParams.set('action', params.action);
      if (params?.limit) searchParams.set('limit', String(params.limit));
      if (params?.offset) searchParams.set('offset', String(params.offset));
      return fetchApi(`/audit/web?${searchParams}`);
    },
  },
};

export { ApiError };
