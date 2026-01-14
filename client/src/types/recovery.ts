/**
 * TypeScript types for loan recovery features.
 * 
 * These types match the Pydantic models in app/models/recovery_models.py
 */

export type DefaultType = 'payment_default' | 'covenant_breach' | 'infraction';
export type DefaultSeverity = 'low' | 'medium' | 'high' | 'critical';
export type DefaultStatus = 'open' | 'in_recovery' | 'resolved' | 'written_off';

export type ActionType = 'sms_reminder' | 'voice_call' | 'email' | 'escalation' | 'legal_notice';
export type CommunicationMethod = 'sms' | 'voice' | 'email';
export type ActionStatus = 'pending' | 'sent' | 'delivered' | 'failed' | 'responded';

export type PreferredContactMethod = 'sms' | 'voice' | 'email';

export interface LoanDefault {
  id: number;
  loan_id: string | null;
  deal_id: number | null;
  default_type: DefaultType;
  default_date: string;
  default_reason: string | null;
  amount_overdue: string | null; // Decimal as string
  days_past_due: number;
  severity: DefaultSeverity;
  status: DefaultStatus;
  resolved_at: string | null;
  cdm_events: Record<string, any>[] | null;
  metadata: Record<string, any> | null;
  created_at: string;
  updated_at: string;
  recovery_actions?: RecoveryAction[];
}

export interface RecoveryAction {
  id: number;
  loan_default_id: number;
  action_type: ActionType;
  communication_method: CommunicationMethod;
  recipient_phone: string | null;
  recipient_email: string | null;
  message_template: string;
  message_content: string;
  twilio_message_sid: string | null;
  twilio_call_sid: string | null;
  status: ActionStatus;
  scheduled_at: string | null;
  sent_at: string | null;
  delivered_at: string | null;
  response_received_at: string | null;
  error_message: string | null;
  created_by: number | null;
  metadata: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

export interface BorrowerContact {
  id: number;
  deal_id: number;
  user_id: number | null;
  contact_name: string;
  phone_number: string | null;
  email: string | null;
  preferred_contact_method: PreferredContactMethod;
  contact_preferences: Record<string, any> | null;
  is_primary: boolean;
  is_active: boolean;
  metadata: Record<string, any> | null;
  created_at: string;
  updated_at: string;
}

// Request/Response types for API calls
export interface DetectDefaultsRequest {
  deal_id?: number | null;
}

export interface RecoveryActionCreate {
  action_types?: string[] | null;
}

export interface BorrowerContactCreate {
  deal_id: number;
  user_id?: number | null;
  contact_name: string;
  phone_number?: string | null;
  email?: string | null;
  preferred_contact_method?: PreferredContactMethod;
  contact_preferences?: Record<string, any> | null;
  is_primary?: boolean;
  is_active?: boolean;
}

export interface BorrowerContactUpdate {
  contact_name?: string | null;
  phone_number?: string | null;
  email?: string | null;
  preferred_contact_method?: PreferredContactMethod | null;
  contact_preferences?: Record<string, any> | null;
  is_primary?: boolean | null;
  is_active?: boolean | null;
}

// List response types
export interface LoanDefaultListResponse {
  defaults: LoanDefault[];
  total: number;
  page: number;
  limit: number;
}

export interface RecoveryActionListResponse {
  actions: RecoveryAction[];
  total: number;
  page: number;
  limit: number;
}

export interface BorrowerContactListResponse {
  contacts: BorrowerContact[];
}
