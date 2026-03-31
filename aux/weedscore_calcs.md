## 1. The Recency Factor ($R$)

This **S-shaped sigmoid curve** introduces a "refractory period" or a "Penalty Zone".

- **The Vibe:** It says, "You smoked yesterday, so for the next few days, you basically have zero credit, no matter what".
    
- **The Formula:**
    
$$R(t) = \frac{100}{1 + e^{-k(t - t_0)}}$$

**Tuning the Shape ($t_0$ and $k$): **The Sigmoid has two knobs: 

- **$t_0 = 14$ (The Midpoint):** This is the day your score hits 50. This is the best way to define your "standard" interval. We can use a value of 14 to begin with and adjust it in future iterations with modeled/cooked data.
    
- **$k = 0.5$ (The Steepness):** Stretches the "S" out for a smoother transition. We can use a value of 0.5 to begin with and adjust it in future iterations with modeled/cooked data. What other values for k do:
	- **High $k$ (e.g., 2.0):** This makes the metric almost binary. You go from "Not Deserved" to "Fully Deserved" in about 48 hours.
    
	- **Low $k$ (e.g., 0.3):** This stretches the "S" out, making the transition from the penalty phase to the recovery phase much smoother.

## 2. Frequency & Clustering Logic

To handle a full year of data, we use a **Hybrid Approach** to separate "Instantaneous Proximity" from "Systemic Momentum".

- **The Cluster Intensity Factor ($C_i$):** Acts as a **High-Pass Filter**. It is highly sensitive to the exact gap between the last two events. It punishes the _speed_ of recurrence.
    
- **The Heat Map ($H$):** Acts as an **Integrator**. It sums the "energy" of all recent events. It punishes the _volume and duration_ of a streak.
    
By multiplying these, we ensure that a long, tight cluster (a "bender") creates a non-linear explosion in debt, while isolated sessions are treated as linear, individual costs.
## A. The Cluster Intensity Factor ($C_i$)

Acts as a **High-Pass Filter**. It punishes the _speed_ of recurrence. For any session $i$, we calculate $C_i$ based on the Inter-Arrival Time ($IAT$) in days since session $i-1$:

$$C_i = 1 + \max\left(0, \frac{T_{threshold} - IAT}{T_{threshold}}\right)^P$$

- **$T_{threshold}$:** 7 days (Our "Danger Zone" window).
    
- **$IAT$:** Days since previous session.
    
- **$P$ (Power):** Initial value **2.0**. A higher $P$ makes the penalty much more severe as the gap approaches 0 days.
    
- **Cold Start Handling:** For the very first session in the database, the $IAT$ is technically undefined. To prevent an arbitrary penalty, the system must **default $IAT$ to 365 days**. This ensures the term inside the bracket is negative, the $\max(0, \dots)$ function returns 0, and $C_i$ evaluates to exactly **1.0**.
    
- **Behavior:** If $IAT \ge 7$, $C_i = 1.0$ (No cluster penalty). If $IAT = 1$, $C_i$ becomes significantly higher, scaling the session's weight.
    

## B. The Heat Accumulation Model ($H$)

Acts as an **Integrator**. It punishes the _volume and duration_ of a streak. The system maintains a "Heat" state variable that determines the "environmental" penalty at the time of a new session.

- **Accumulation:** Each session adds **+10 units** of Heat.
    
- **Dissipation:** Heat decays at a rate of **-1 unit per day** (Floor at 0).
    
- **The Weighting Effect:** The Weight of session $i$ is scaled by the Heat level _at the moment the session occurs_.
    
    - _Example:_ If you have 15 units of Heat from a previous cluster and smoke again, that session is 1.5x more "expensive."
    

## 3. Categorical Multipliers & Annual Decay

- **Solo Multiplier ($S$):** A static coefficient of **1.5** applied to the session weight if the `is_solo` flag is TRUE.
    
- **Annual Decay ($L$):** To track the "20 sessions per year" limit, we use a **Linear Decay** over 365 days.
    
    - $L = \max(0, 1 - \frac{\text{DaysSinceEvent}}{365})$
        
    - _Note:_ This ensures an event from 11 months ago still "counts" toward your annual debt, but only carries ~8% of its original weight.

## 4. Final Frequency Debt Integration ($D$)

The total Debt ($D$) at any timestamp $T$ is the sum of all historic sessions in a rolling 365-day window.

$$D = \sum_{i=1}^{n} (\text{BaseWeight} \times C_i \times H_i \times S_i \times L_i)$$

- This $D$ value is the denominator that suppresses your **Sigmoid Recovery Score**.
- **BaseWeight:** We can use a value of 10.0 to begin with and adjust it in future iterations with modeled/cooked data.
    

## 5. The Final Integration: The Weedscore ($W$)

The total Weedscore suppresses the Short-Term Recovery ($R$) by the Long-Term Debt ($D$). We use a **Sensitivity Constant (K)** to ensure the 0-100 range remains meaningful. We set it to K = 150 to begin with.

$$W = \text{round}\left(\frac{R(t)}{1 + (D / K)}, 2\right)$$

- **The Balancing Act:** Even if you wait 3 weeks ($R \approx 100$), a high $D$ from a previous "Bender" will mathematically cap your final score.
    
- **Occasion Boost:** If `is_special_occasion` is TRUE, $W = W \times 1.5$ (Capped at 100.0).

**Logic of the Compound Metric:**

- **The Balancing Act:** While $R(t)$ represents your short-term "worthiness" based on the single most recent event, $D$ represents the long-term "cost" of your lifestyle.
    
- **The Ceiling Effect:** In a scenario with high frequency or heavy clustering, $D$ grows large. Even if you wait 3 weeks (making $R(t) \approx 100$), the high value of $D$ will mathematically "cap" your final score. This prevents the user from "resetting" a bad month with just a few days of abstinence.
    
- **The Reward for Moderation:** As your annual frequency decreases and clusters dissipate, $D$ trends toward 0. Only when $D$ is near 0 can the Weedscore ($W$) actually approach its maximum theoretical value of 100.

**---------------------------**

**Configurable parameters (degrees of freedom)**

To personalise the Weedscore formula across different use cases, we can manipulate several "knobs" that control everything from short-term discipline to long-term lifestyle costs.

## 1. Short-Term Recovery Parameters ($R$)

These constants define the "refractory period" immediately following a session.

- **Midpoint ($t_0$):** Set to **14.0 days**. This is the "standard interval"; it is the exact day the recovery score hits 50/100.
    
- **Steepness ($k$):** Set to **0.5**. A higher value (e.g., 2.0) makes the recovery feel like a "switch" that flips on after the penalty zone, while a lower value (e.g., 0.2) makes the recovery feel very gradual.
    

## 2. Clustering & Proximity Parameters ($C_i$)

These control how severely the system punishes "back-to-back" sessions or streaks.

- **Threshold ($T_{threshold}$):** Set to **7.0 days**. Any sessions occurring closer together than this window trigger a non-linear penalty.
    
- **Penalty Power ($P$):** Set to **2.0**. This determines the "aggression" of the cluster penalty as the gap between sessions approaches zero.
    
- **Cold Start Default ($IAT$):** Set to **365.0 days**. This ensures the very first session in a clean database carries no cluster penalty.
    

## 3. Systemic "Heat" Parameters ($H$)

This simulates "momentum" or a "bender" by tracking recent volume.

- **Heat Accumulation:** Set to **+10.0 units** per session. This is the "cost" added to the internal heat state every time you smoke.
    
- **Heat Dissipation:** Set to **-1.0 unit per day**. This is the rate at which the "environmental penalty" cools down during abstinence.
    
- **Heat Scaling:** Currently implemented as `current_heat / 10.0`. This means every 10 units of heat adds a 1.0x multiplier to the next session's debt.
    

## 4. Long-Term Debt & Weighting ($D$)

These parameters define the "cost" of your history over a rolling year.

- **Base Weight:** Set to **10.0**. The starting cost of a single, isolated, non-solo session.
    
- **Solo Multiplier ($S$):** Set to **1.5**. The penalty coefficient applied if you are not in a social setting.
    
- **Annual Window:** Set to **365 days**. The look-back period for calculating total frequency debt.
    
- **Decay Rate ($L$):** Linearly reduces a session's impact from 100% to 0% over the 365-day window.
    

## 5. Integration & Sensitivity ($W$)

This controls the final output range.

- **Sensitivity Constant ($K$):** Set to **150.0**. This is the most powerful "global" knob; it scales the total debt to ensure the final score stays meaningful for a target of ~30 sessions per year.
    
- **Special Occasion Boost:** Set to **1.5**. A multiplier applied to the _final_ score to bypass restrictions for holidays or events.
