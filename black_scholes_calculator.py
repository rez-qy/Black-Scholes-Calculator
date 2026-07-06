"""
Black-Scholes Options Pricing Calculator
=========================================
A professional implementation of the Black-Scholes model for pricing
European call and put options, including Greeks calculation.

"""

import math
from scipy.stats import norm


# ─────────────────────────────────────────────
# Core Black-Scholes Functions
# ─────────────────────────────────────────────

def d1(S, K, T, r, sigma):
    """
    Calculate d1 component of the Black-Scholes formula.
    Parameters:
        S     : Current stock price
        K     : Strike price
        T     : Time to expiration (in years)
        r     : Risk-free interest rate (annual, decimal)
        sigma : Volatility of the underlying asset (annual, decimal)
    """
    return (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))


def d2(S, K, T, r, sigma):
    """Calculate d2 component of the Black-Scholes formula."""
    return d1(S, K, T, r, sigma) - sigma * math.sqrt(T)


def black_scholes_call(S, K, T, r, sigma):
    """
    Calculate the price of a European Call Option.
    Returns:
        float: Call option price
    """
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)
    price = S * norm.cdf(_d1) - K * math.exp(-r * T) * norm.cdf(_d2)
    return price


def black_scholes_put(S, K, T, r, sigma):
    """
    Calculate the price of a European Put Option.
    Uses put-call parity: P = C - S + K * e^(-rT)
    Returns:
        float: Put option price
    """
    call = black_scholes_call(S, K, T, r, sigma)
    put = call - S + K * math.exp(-r * T)
    return put


# ─────────────────────────────────────────────
# Greeks Calculation
# ─────────────────────────────────────────────

def calculate_greeks(S, K, T, r, sigma):
    """
    Calculate the Option Greeks for both call and put.

    Greeks measure sensitivity of option price to various factors:
        Delta  : Sensitivity to underlying price change
        Gamma  : Rate of change of Delta
        Theta  : Time decay (per calendar day)
        Vega   : Sensitivity to volatility change (per 1% move)
        Rho    : Sensitivity to interest rate change (per 1% move)

    Returns:
        dict: Dictionary containing call and put Greeks
    """
    _d1 = d1(S, K, T, r, sigma)
    _d2 = d2(S, K, T, r, sigma)

    # Delta
    call_delta = norm.cdf(_d1)
    put_delta  = call_delta - 1

    # Gamma (same for call and put)
    gamma = norm.pdf(_d1) / (S * sigma * math.sqrt(T))

    # Theta (annualised, then divided by 365 for daily)
    call_theta = (
        -(S * norm.pdf(_d1) * sigma) / (2 * math.sqrt(T))
        - r * K * math.exp(-r * T) * norm.cdf(_d2)
    ) / 365

    put_theta = (
        -(S * norm.pdf(_d1) * sigma) / (2 * math.sqrt(T))
        + r * K * math.exp(-r * T) * norm.cdf(-_d2)
    ) / 365

    # Vega (per 1% change in volatility)
    vega = S * norm.pdf(_d1) * math.sqrt(T) / 100

    # Rho (per 1% change in interest rate)
    call_rho = K * T * math.exp(-r * T) * norm.cdf(_d2)  / 100
    put_rho  = -K * T * math.exp(-r * T) * norm.cdf(-_d2) / 100

    return {
        "call": {
            "delta": call_delta,
            "gamma": gamma,
            "theta": call_theta,
            "vega":  vega,
            "rho":   call_rho,
        },
        "put": {
            "delta": put_delta,
            "gamma": gamma,
            "theta": put_theta,
            "vega":  vega,
            "rho":   put_rho,
        }
    }


# ─────────────────────────────────────────────
# Input Validation
# ─────────────────────────────────────────────

def validate_inputs(S, K, T, r, sigma):
    """Validate all input parameters and raise informative errors."""
    if S <= 0:
        raise ValueError(f"Stock price (S) must be positive. Got: {S}")
    if K <= 0:
        raise ValueError(f"Strike price (K) must be positive. Got: {K}")
    if T <= 0:
        raise ValueError(f"Time to expiry (T) must be positive. Got: {T}")
    if sigma <= 0:
        raise ValueError(f"Volatility (sigma) must be positive. Got: {sigma}")
    if not (0 <= r <= 1):
        raise ValueError(f"Risk-free rate (r) should be between 0 and 1. Got: {r}")


# ─────────────────────────────────────────────
# Results Display
# ─────────────────────────────────────────────

def display_results(S, K, T, r, sigma):
    """
    Run the full Black-Scholes calculation and print a formatted report.
    """
    validate_inputs(S, K, T, r, sigma)

    call_price = black_scholes_call(S, K, T, r, sigma)
    put_price  = black_scholes_put(S, K, T, r, sigma)
    greeks     = calculate_greeks(S, K, T, r, sigma)

    # Moneyness label
    if S > K:
        moneyness = "In-the-Money (ITM)"
    elif S < K:
        moneyness = "Out-of-the-Money (OTM)"
    else:
        moneyness = "At-the-Money (ATM)"

    print("=" * 55)
    print("     BLACK-SCHOLES OPTIONS PRICING CALCULATOR")
    print("=" * 55)

    print("\n📥  INPUT PARAMETERS")
    print(f"    Stock Price (S)       : £{S:>10.2f}")
    print(f"    Strike Price (K)      : £{K:>10.2f}")
    print(f"    Time to Expiry (T)    : {T:>10.4f} years  ({T*365:.0f} days)")
    print(f"    Risk-Free Rate (r)    : {r*100:>9.2f}%")
    print(f"    Volatility (σ)        : {sigma*100:>9.2f}%")
    print(f"    Moneyness             :  {moneyness}")

    print("\n💰  OPTION PRICES")
    print(f"    Call Option Price     : £{call_price:>10.4f}")
    print(f"    Put Option Price      : £{put_price:>10.4f}")

    # Verify put-call parity
    parity_check = call_price - put_price - S + K * math.exp(-r * T)
    print(f"\n    ✅ Put-Call Parity Check  : {parity_check:.6f}  (should be ~0)")

    print("\n📐  OPTION GREEKS")
    print(f"  {'Greek':<12} {'Call':>12} {'Put':>12}   Description")
    print(f"  {'-'*12} {'-'*12} {'-'*12}   {'-'*30}")

    g = greeks
    print(f"  {'Delta':<12} {g['call']['delta']:>12.4f} {g['put']['delta']:>12.4f}   Price sensitivity to S")
    print(f"  {'Gamma':<12} {g['call']['gamma']:>12.4f} {g['put']['gamma']:>12.4f}   Delta sensitivity to S")
    print(f"  {'Theta':<12} {g['call']['theta']:>12.4f} {g['put']['theta']:>12.4f}   Daily time decay (£/day)")
    print(f"  {'Vega':<12} {g['call']['vega']:>12.4f} {g['put']['vega']:>12.4f}   Price change per 1% vol")
    print(f"  {'Rho':<12} {g['call']['rho']:>12.4f} {g['put']['rho']:>12.4f}   Price change per 1% rate")

    print("\n" + "=" * 55)
    print("  Note: Prices in £. Theta is per calendar day.")
    print("  Model assumes European options with no dividends.")
    print("=" * 55)

    return {
        "call_price": call_price,
        "put_price":  put_price,
        "greeks":     greeks
    }


# ─────────────────────────────────────────────
# Interactive CLI
# ─────────────────────────────────────────────

def get_float_input(prompt, min_val=None, max_val=None):
    """Helper to get validated float input from user."""
    while True:
        try:
            value = float(input(prompt))
            if min_val is not None and value <= min_val:
                print(f"  ⚠️  Value must be greater than {min_val}. Try again.")
                continue
            if max_val is not None and value > max_val:
                print(f"  ⚠️  Value must be ≤ {max_val}. Try again.")
                continue
            return value
        except ValueError:
            print("  ⚠️  Please enter a valid number.")


def run_interactive():
    """Launch an interactive command-line interface."""
    print("\n" + "=" * 55)
    print("   BLACK-SCHOLES OPTIONS PRICING CALCULATOR")
    print("   Enter parameters below (press Ctrl+C to quit)")
    print("=" * 55)

    while True:
        print()
        try:
            S     = get_float_input("  Stock Price        (S)  £ : ", min_val=0)
            K     = get_float_input("  Strike Price       (K)  £ : ", min_val=0)
            T_days = get_float_input("  Days to Expiry         : ", min_val=0)
            T     = T_days / 365
            r     = get_float_input("  Risk-Free Rate   (r)  % : ", min_val=0, max_val=100) / 100
            sigma = get_float_input("  Volatility       (σ)  % : ", min_val=0, max_val=200) / 100

            print()
            display_results(S, K, T, r, sigma)

        except ValueError as e:
            print(f"\n  ❌ Input Error: {e}")
        except KeyboardInterrupt:
            print("\n\n  Goodbye!\n")
            break

        print("\n  Run another calculation? (press Enter to continue, Ctrl+C to quit)")
        input()


# ─────────────────────────────────────────────
# Example Usage / Demo
# ─────────────────────────────────────────────

def run_demo():
    """
    Run a demo with example parameters to showcase the calculator.
    Useful for testing and demonstrating the tool on a CV / portfolio.
    """
    print("\n--- DEMO: Apple Inc. (AAPL) Option ---")
    display_results(
        S     = 175.00,   # Current stock price
        K     = 180.00,   # Strike price
        T     = 30 / 365, # 30 days to expiry
        r     = 0.053,    # 5.3% risk-free rate
        sigma = 0.28      # 28% implied volatility
    )

    print("\n--- DEMO: Deep In-the-Money Call ---")
    display_results(
        S     = 200.00,
        K     = 150.00,
        T     = 90 / 365,
        r     = 0.05,
        sigma = 0.20
    )


# ─────────────────────────────────────────────
# Entry Point
# ─────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        run_demo()
    else:
        run_interactive()