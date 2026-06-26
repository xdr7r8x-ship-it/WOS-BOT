from enum import Enum


class ErrorType(Enum):
    NETWORK_ERROR = "NETWORK_ERROR"
    TIMEOUT = "TIMEOUT"
    RATE_LIMIT = "RATE_LIMIT"
    TEMPORARY_API_ERROR = "TEMPORARY_API_ERROR"
    DATABASE_LOCKED = "DATABASE_LOCKED"
    DISCORD_SEND_FAILED = "DISCORD_SEND_FAILED"
    CAPTCHA_REQUIRED = "CAPTCHA_REQUIRED"
    HUMAN_VERIFICATION_REQUIRED = "HUMAN_VERIFICATION_REQUIRED"
    INVALID_CODE = "INVALID_CODE"
    EXPIRED_CODE = "EXPIRED_CODE"
    ALREADY_REDEEMED = "ALREADY_REDEEMED"
    INVALID_PLAYER_ID = "INVALID_PLAYER_ID"
    UNKNOWN_ERROR = "UNKNOWN_ERROR"


class RedemptionStatus(Enum):
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    SKIPPED_DUPLICATE = "SKIPPED_DUPLICATE"
    RETRY_LATER = "RETRY_LATER"
    RATE_LIMITED = "RATE_LIMITED"
    TIMEOUT = "TIMEOUT"
    NETWORK_ERROR = "NETWORK_ERROR"
    INVALID_PLAYER_ID = "INVALID_PLAYER_ID"
    INVALID_CODE = "INVALID_CODE"
    EXPIRED_CODE = "EXPIRED_CODE"
    ALREADY_REDEEMED = "ALREADY_REDEEMED"
    NEEDS_VERIFICATION = "NEEDS_VERIFICATION"


RETRYABLE_ERRORS = {
    ErrorType.NETWORK_ERROR,
    ErrorType.TIMEOUT,
    ErrorType.RATE_LIMIT,
    ErrorType.TEMPORARY_API_ERROR,
    ErrorType.DATABASE_LOCKED,
    ErrorType.DISCORD_SEND_FAILED,
    ErrorType.UNKNOWN_ERROR,
}

FINAL_ERRORS = {
    ErrorType.INVALID_CODE,
    ErrorType.EXPIRED_CODE,
    ErrorType.ALREADY_REDEEMED,
    ErrorType.INVALID_PLAYER_ID,
    ErrorType.CAPTCHA_REQUIRED,
    ErrorType.HUMAN_VERIFICATION_REQUIRED,
}


def is_retryable(error_type: ErrorType) -> bool:
    return error_type in RETRYABLE_ERRORS


def is_final_error(error_type: ErrorType) -> bool:
    return error_type in FINAL_ERRORS


def get_redemption_status(error_type: ErrorType) -> RedemptionStatus:
    mapping = {
        ErrorType.NETWORK_ERROR: RedemptionStatus.NETWORK_ERROR,
        ErrorType.TIMEOUT: RedemptionStatus.TIMEOUT,
        ErrorType.RATE_LIMIT: RedemptionStatus.RATE_LIMITED,
        ErrorType.TEMPORARY_API_ERROR: RedemptionStatus.FAILED,
        ErrorType.DATABASE_LOCKED: RedemptionStatus.RETRY_LATER,
        ErrorType.DISCORD_SEND_FAILED: RedemptionStatus.FAILED,
        ErrorType.CAPTCHA_REQUIRED: RedemptionStatus.NEEDS_VERIFICATION,
        ErrorType.HUMAN_VERIFICATION_REQUIRED: RedemptionStatus.NEEDS_VERIFICATION,
        ErrorType.INVALID_CODE: RedemptionStatus.INVALID_CODE,
        ErrorType.EXPIRED_CODE: RedemptionStatus.EXPIRED_CODE,
        ErrorType.ALREADY_REDEEMED: RedemptionStatus.ALREADY_REDEEMED,
        ErrorType.INVALID_PLAYER_ID: RedemptionStatus.INVALID_PLAYER_ID,
        ErrorType.UNKNOWN_ERROR: RedemptionStatus.FAILED,
    }
    return mapping.get(error_type, RedemptionStatus.FAILED)
