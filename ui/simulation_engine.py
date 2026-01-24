"""
StockAI Simulation Engine
=========================
Bridge between the UI and the backend simulation logic.
Provides a clean interface for running and managing simulations.
"""

import sys
import os
import random
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===============================
# DATA CLASSES
# ===============================

@dataclass
class AgentState:
    """Represents the current state of an agent."""
    id: int
    name: str
    character: str  # Conservative, Aggressive, Balanced, Growth-Oriented
    cash: float
    stock_a_amount: int
    stock_b_amount: int
    total_value: float
    initial_value: float
    pnl_percent: float
    loans: List[Dict]
    is_bankrupt: bool
    quit: bool
    action_history: List[Dict] = field(default_factory=list)
    
    # Behavioral biases (simulated based on character and market conditions)
    herding_level: str = "Low"  # Low, Medium, High
    loss_aversion_level: str = "Medium"
    overconfidence_level: str = "Low"
    anchoring_level: str = "Medium"


@dataclass
class StockState:
    """Represents the current state of a stock."""
    name: str
    price: float
    initial_price: float
    price_history: List[Dict] = field(default_factory=list)  # [{day, session, price}]
    
    @property
    def change_percent(self) -> float:
        if self.initial_price == 0:
            return 0
        return ((self.price - self.initial_price) / self.initial_price) * 100


@dataclass
class MarketEvent:
    """Represents a market event."""
    day: int
    event_type: str  # "macro", "sentiment", "corporate"
    title: str
    description: str
    severity: str  # "LOW", "MEDIUM", "HIGH"
    impact: str  # Description of market impact


@dataclass
class TradeRecord:
    """Represents a completed trade."""
    day: int
    session: int
    stock: str
    buyer_id: int
    seller_id: int
    amount: int
    price: float


@dataclass 
class ForumMessage:
    """Represents a BBS forum message from an agent."""
    day: int
    agent_id: int
    agent_name: str
    message: str
    sentiment: str  # "bullish", "bearish", "neutral"


@dataclass
class SimulationState:
    """Complete simulation state."""
    # Status
    status: str = "IDLE"  # IDLE, CONFIGURED, RUNNING, PAUSED, COMPLETED
    run_id: Optional[str] = None
    current_day: int = 0
    current_session: int = 0
    
    # Configuration
    agent_count: int = 50
    total_days: int = 30
    sessions_per_day: int = 3
    volatility: str = "Medium"
    event_intensity: int = 5
    loan_market_enabled: bool = True
    random_seed: int = 42
    
    # Data
    agents: List[AgentState] = field(default_factory=list)
    stock_a: Optional[StockState] = None
    stock_b: Optional[StockState] = None
    events: List[MarketEvent] = field(default_factory=list)
    trades: List[TradeRecord] = field(default_factory=list)
    forum_messages: List[ForumMessage] = field(default_factory=list)
    
    # Metrics
    total_capital: float = 0
    active_agents: int = 0
    total_trades: int = 0
    market_sentiment: str = "neutral"  # bullish, bearish, neutral
    herding_percentage: float = 0
    system_risk: str = "LOW"


# ===============================
# AGENT NAME GENERATOR
# ===============================

AGENT_PREFIXES = [
    "Alpha", "Beta", "Gamma", "Delta", "Epsilon", "Zeta", "Eta", "Theta",
    "Atlas", "Beacon", "Cipher", "Drift", "Echo", "Flux", "Grid", "Helix",
    "Ion", "Jade", "Kappa", "Luna", "Maven", "Nexus", "Orion", "Pulse",
    "Quasar", "Raven", "Sigma", "Titan", "Unity", "Vector", "Wave", "Xenon",
    "Yield", "Zenith", "Apex", "Blaze", "Core", "Dash", "Edge", "Frost"
]

def generate_agent_name(agent_id: int) -> str:
    """Generate a unique agent name."""
    prefix = AGENT_PREFIXES[agent_id % len(AGENT_PREFIXES)]
    suffix = (agent_id // len(AGENT_PREFIXES)) + 1
    return f"{prefix}-{suffix:02d}"


# ===============================
# SIMULATION ENGINE
# ===============================

class SimulationEngine:
    """
    Main simulation engine that manages the market simulation.
    This is a simplified version that runs without LLM calls.
    """
    
    def __init__(self):
        self.state = SimulationState()
        self._random = random.Random()
    
    def configure(self, 
                  agent_count: int = 50,
                  total_days: int = 30,
                  volatility: str = "Medium",
                  event_intensity: int = 5,
                  loan_market_enabled: bool = True,
                  random_seed: int = 42) -> SimulationState:
        """Configure the simulation parameters."""
        
        self._random.seed(random_seed)
        random.seed(random_seed)
        
        self.state = SimulationState(
            status="CONFIGURED",
            run_id=f"RUN-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            agent_count=agent_count,
            total_days=total_days,
            volatility=volatility,
            event_intensity=event_intensity,
            loan_market_enabled=loan_market_enabled,
            random_seed=random_seed,
        )
        
        # Initialize stocks
        self.state.stock_a = StockState(
            name="A",
            price=30.0,
            initial_price=30.0,
            price_history=[{"day": 0, "session": 0, "price": 30.0}]
        )
        
        self.state.stock_b = StockState(
            name="B", 
            price=40.0,
            initial_price=40.0,
            price_history=[{"day": 0, "session": 0, "price": 40.0}]
        )
        
        # Initialize agents
        self.state.agents = []
        characters = ["Conservative", "Aggressive", "Balanced", "Growth-Oriented"]
        
        for i in range(agent_count):
            # Random initial portfolio
            cash = self._random.uniform(100000, 500000)
            stock_a = self._random.randint(50, 500)
            stock_b = self._random.randint(50, 500)
            character = characters[i % len(characters)]
            
            initial_value = cash + stock_a * 30.0 + stock_b * 40.0
            
            # Initialize loans based on character
            loans = []
            if self._random.random() < 0.3:  # 30% chance of initial loan
                loans.append({
                    "loan": "yes",
                    "amount": self._random.uniform(50000, 200000),
                    "loan_type": self._random.randint(0, 2),
                    "repayment_date": self._random.choice([22, 44, 66])
                })
            
            agent = AgentState(
                id=i,
                name=generate_agent_name(i),
                character=character,
                cash=cash,
                stock_a_amount=stock_a,
                stock_b_amount=stock_b,
                total_value=initial_value,
                initial_value=initial_value,
                pnl_percent=0.0,
                loans=loans,
                is_bankrupt=False,
                quit=False,
                herding_level=self._random.choice(["Low", "Medium", "High"]),
                loss_aversion_level=self._random.choice(["Low", "Medium", "High"]),
                overconfidence_level=self._random.choice(["Low", "Medium", "High"]),
                anchoring_level=self._random.choice(["Low", "Medium", "High"]),
            )
            self.state.agents.append(agent)
        
        # Generate events based on intensity
        self._generate_events()
        
        # Calculate initial metrics
        self._update_metrics()
        
        return self.state
    
    def _generate_events(self):
        """Generate market events based on event intensity."""
        self.state.events = []
        
        # Base events that always happen
        base_events = [
            MarketEvent(
                day=max(1, self.state.total_days // 4),
                event_type="macro",
                title="Interest Rate Decision",
                description="Central bank announces monetary policy decision",
                severity="MEDIUM",
                impact="Market volatility expected around announcement"
            ),
            MarketEvent(
                day=max(1, self.state.total_days // 2),
                event_type="corporate",
                title="Earnings Season",
                description="Major companies release quarterly earnings",
                severity="MEDIUM", 
                impact="Stock-specific movements expected"
            ),
        ]
        
        self.state.events.extend(base_events)
        
        # Additional events based on intensity
        num_additional = self.state.event_intensity - 2
        
        event_templates = [
            ("macro", "Policy Announcement", "Government announces new economic policy", "HIGH"),
            ("macro", "Trade Agreement", "New international trade deal signed", "MEDIUM"),
            ("sentiment", "Market Sentiment Shift", "Investor sentiment turns cautious", "MEDIUM"),
            ("sentiment", "Social Media Buzz", "Viral discussion affects market perception", "LOW"),
            ("corporate", "M&A Announcement", "Major merger/acquisition announced", "HIGH"),
            ("corporate", "Product Launch", "Company announces new product line", "LOW"),
            ("macro", "Economic Data Release", "Key economic indicators published", "MEDIUM"),
            ("sentiment", "Analyst Downgrade", "Major analyst downgrades sector outlook", "MEDIUM"),
        ]
        
        used_days = set(e.day for e in self.state.events)
        
        for i in range(max(0, num_additional)):
            template = self._random.choice(event_templates)
            
            # Find unused day
            day = self._random.randint(1, self.state.total_days)
            attempts = 0
            while day in used_days and attempts < 20:
                day = self._random.randint(1, self.state.total_days)
                attempts += 1
            
            used_days.add(day)
            
            self.state.events.append(MarketEvent(
                day=day,
                event_type=template[0],
                title=template[1],
                description=template[2],
                severity=template[3],
                impact=f"Expected {template[3].lower()} impact on market dynamics"
            ))
        
        # Sort by day
        self.state.events.sort(key=lambda e: e.day)
    
    def _update_metrics(self):
        """Update simulation metrics based on current state."""
        active = [a for a in self.state.agents if not a.quit and not a.is_bankrupt]
        self.state.active_agents = len(active)
        
        if active:
            self.state.total_capital = sum(a.total_value for a in active)
            
            # Calculate herding percentage
            characters = [a.character for a in active]
            most_common = max(set(characters), key=characters.count)
            self.state.herding_percentage = (characters.count(most_common) / len(active)) * 100
            
            # Determine market sentiment from price trends
            if self.state.stock_a and len(self.state.stock_a.price_history) > 1:
                recent_prices = [p["price"] for p in self.state.stock_a.price_history[-5:]]
                if len(recent_prices) >= 2:
                    trend = recent_prices[-1] - recent_prices[0]
                    if trend > 1:
                        self.state.market_sentiment = "bullish"
                    elif trend < -1:
                        self.state.market_sentiment = "bearish"
                    else:
                        self.state.market_sentiment = "neutral"
            
            # Calculate system risk
            volatility_scores = {"Low": 1, "Medium": 2, "High": 3, "Extreme": 4}
            vol_score = volatility_scores.get(self.state.volatility, 2)
            
            bankruptcies = len([a for a in self.state.agents if a.is_bankrupt])
            bankruptcy_rate = bankruptcies / self.state.agent_count
            
            risk_score = vol_score + (self.state.event_intensity / 3) + (bankruptcy_rate * 5)
            
            if risk_score < 4:
                self.state.system_risk = "LOW"
            elif risk_score < 7:
                self.state.system_risk = "ELEVATED"
            else:
                self.state.system_risk = "HIGH"
    
    def run_day(self) -> SimulationState:
        """Run a single simulation day (all sessions)."""
        if self.state.status not in ["CONFIGURED", "RUNNING", "PAUSED"]:
            return self.state
        
        self.state.status = "RUNNING"
        self.state.current_day += 1
        
        # Check for events today
        today_events = [e for e in self.state.events if e.day == self.state.current_day]
        
        # Volatility multiplier based on settings and events
        volatility_mult = {
            "Low": 0.01,
            "Medium": 0.02,
            "High": 0.035,
            "Extreme": 0.05
        }.get(self.state.volatility, 0.02)
        
        # Increase volatility on event days
        if today_events:
            volatility_mult *= 1.5
        
        # Run 3 trading sessions
        for session in range(1, 4):
            self.state.current_session = session
            self._run_session(volatility_mult, today_events)
        
        # End of day processing
        self._process_end_of_day()
        
        # Generate forum messages (BBS)
        self._generate_forum_messages()
        
        # Check if simulation is complete
        if self.state.current_day >= self.state.total_days:
            self.state.status = "COMPLETED"
        
        return self.state
    
    def _run_session(self, volatility_mult: float, events: List[MarketEvent]):
        """Run a single trading session."""
        
        # Update stock prices with random walk + event impact
        event_impact = 0
        if events:
            for event in events:
                if event.severity == "HIGH":
                    event_impact = self._random.uniform(-0.03, 0.03)
                elif event.severity == "MEDIUM":
                    event_impact = self._random.uniform(-0.015, 0.015)
                else:
                    event_impact = self._random.uniform(-0.005, 0.005)
        
        # Stock A price update
        change_a = self._random.gauss(0, volatility_mult) + event_impact * 0.7
        self.state.stock_a.price = max(1, self.state.stock_a.price * (1 + change_a))
        self.state.stock_a.price_history.append({
            "day": self.state.current_day,
            "session": self.state.current_session,
            "price": self.state.stock_a.price
        })
        
        # Stock B price update (more volatile)
        change_b = self._random.gauss(0, volatility_mult * 1.3) + event_impact
        self.state.stock_b.price = max(1, self.state.stock_b.price * (1 + change_b))
        self.state.stock_b.price_history.append({
            "day": self.state.current_day,
            "session": self.state.current_session,
            "price": self.state.stock_b.price
        })
        
        # Simulate agent trading
        active_agents = [a for a in self.state.agents if not a.quit and not a.is_bankrupt]
        self._random.shuffle(active_agents)
        
        for agent in active_agents:
            self._simulate_agent_action(agent)
        
        # Update agent values
        for agent in self.state.agents:
            if not agent.quit:
                agent.total_value = (
                    agent.cash + 
                    agent.stock_a_amount * self.state.stock_a.price +
                    agent.stock_b_amount * self.state.stock_b.price
                )
                agent.pnl_percent = ((agent.total_value - agent.initial_value) / agent.initial_value) * 100
    
    def _simulate_agent_action(self, agent: AgentState):
        """Simulate a trading action for an agent (without LLM)."""
        
        # Decision based on character and market conditions
        action_prob = self._random.random()
        
        # Character-based trading tendency
        if agent.character == "Conservative":
            buy_threshold = 0.7
            sell_threshold = 0.2
            trade_size_mult = 0.1
        elif agent.character == "Aggressive":
            buy_threshold = 0.4
            sell_threshold = 0.5
            trade_size_mult = 0.3
        elif agent.character == "Growth-Oriented":
            buy_threshold = 0.5
            sell_threshold = 0.3
            trade_size_mult = 0.2
        else:  # Balanced
            buy_threshold = 0.55
            sell_threshold = 0.35
            trade_size_mult = 0.15
        
        # Adjust based on market sentiment
        if self.state.market_sentiment == "bullish":
            buy_threshold -= 0.1
        elif self.state.market_sentiment == "bearish":
            sell_threshold += 0.1
        
        # Determine action
        if action_prob > buy_threshold and agent.cash > 1000:
            # Buy
            stock = "A" if self._random.random() > 0.4 else "B"
            price = self.state.stock_a.price if stock == "A" else self.state.stock_b.price
            max_amount = int((agent.cash * trade_size_mult) / price)
            
            if max_amount > 0:
                amount = self._random.randint(1, max(1, max_amount))
                cost = amount * price
                
                if cost <= agent.cash:
                    agent.cash -= cost
                    if stock == "A":
                        agent.stock_a_amount += amount
                    else:
                        agent.stock_b_amount += amount
                    
                    agent.action_history.append({
                        "day": self.state.current_day,
                        "session": self.state.current_session,
                        "action": "BUY",
                        "stock": stock,
                        "amount": amount,
                        "price": price,
                        "reasoning": self._generate_reasoning(agent, "BUY", stock)
                    })
                    
        elif action_prob < sell_threshold:
            # Sell
            stock = "A" if self._random.random() > 0.4 else "B"
            holdings = agent.stock_a_amount if stock == "A" else agent.stock_b_amount
            
            if holdings > 0:
                amount = self._random.randint(1, max(1, int(holdings * trade_size_mult)))
                price = self.state.stock_a.price if stock == "A" else self.state.stock_b.price
                
                if stock == "A":
                    agent.stock_a_amount -= amount
                else:
                    agent.stock_b_amount -= amount
                agent.cash += amount * price
                
                agent.action_history.append({
                    "day": self.state.current_day,
                    "session": self.state.current_session,
                    "action": "SELL",
                    "stock": stock,
                    "amount": amount,
                    "price": price,
                    "reasoning": self._generate_reasoning(agent, "SELL", stock)
                })
    
    def _generate_reasoning(self, agent: AgentState, action: str, stock: str) -> str:
        """Generate a reasoning explanation for an agent's action."""
        
        reasons = {
            "BUY": [
                f"Bullish on {stock} based on recent price momentum",
                f"Undervalued relative to fundamentals",
                f"Following market sentiment indicators",
                f"Portfolio rebalancing - increasing {stock} exposure",
                f"Technical indicators suggest upward trend",
                f"Contrarian play after recent dip",
            ],
            "SELL": [
                f"Taking profits on {stock} position",
                f"Risk management - reducing exposure",
                f"Bearish outlook based on macro conditions",
                f"Portfolio rebalancing - decreasing {stock} weight",
                f"Stop-loss triggered by price movement",
                f"Liquidity needs for other opportunities",
            ]
        }
        
        base_reason = self._random.choice(reasons.get(action, ["Market analysis"]))
        
        # Add character-specific context
        if agent.character == "Conservative":
            base_reason += " (conservative risk approach)"
        elif agent.character == "Aggressive":
            base_reason += " (aggressive growth strategy)"
        
        return base_reason
    
    def _process_end_of_day(self):
        """Process end-of-day activities."""
        
        # Check for loan repayments
        if self.state.loan_market_enabled:
            for agent in self.state.agents:
                if agent.quit or agent.is_bankrupt:
                    continue
                
                for loan in agent.loans[:]:
                    if loan.get("repayment_date") == self.state.current_day:
                        repayment = loan["amount"] * 1.03  # 3% interest
                        agent.cash -= repayment
                        agent.loans.remove(loan)
                        
                        if agent.cash < 0:
                            # Bankruptcy check
                            total_stock_value = (
                                agent.stock_a_amount * self.state.stock_a.price +
                                agent.stock_b_amount * self.state.stock_b.price
                            )
                            if total_stock_value + agent.cash < 0:
                                agent.is_bankrupt = True
                            else:
                                # Forced liquidation
                                self._force_liquidation(agent)
        
        # Update metrics
        self._update_metrics()
    
    def _force_liquidation(self, agent: AgentState):
        """Force liquidation of agent's positions to cover debt."""
        while agent.cash < 0 and (agent.stock_a_amount > 0 or agent.stock_b_amount > 0):
            if agent.stock_a_amount > 0:
                sell_amount = min(agent.stock_a_amount, 
                                 max(1, int(-agent.cash / self.state.stock_a.price) + 1))
                agent.stock_a_amount -= sell_amount
                agent.cash += sell_amount * self.state.stock_a.price
            elif agent.stock_b_amount > 0:
                sell_amount = min(agent.stock_b_amount,
                                 max(1, int(-agent.cash / self.state.stock_b.price) + 1))
                agent.stock_b_amount -= sell_amount
                agent.cash += sell_amount * self.state.stock_b.price
    
    def _generate_forum_messages(self):
        """Generate BBS forum messages for the day."""
        
        # Select random agents to post
        active_agents = [a for a in self.state.agents if not a.quit and not a.is_bankrupt]
        posters = self._random.sample(active_agents, min(5, len(active_agents)))
        
        message_templates = {
            "bullish": [
                "Market looking strong today! 📈",
                "Great buying opportunity in the current dip",
                "Technical indicators are all pointing up",
                "Fundamentals remain solid despite volatility",
                "Loading up on more shares today",
            ],
            "bearish": [
                "Taking some profits here, be careful 📉",
                "Market seems overextended, staying cautious",
                "Not liking the macro headwinds",
                "Reducing exposure until clarity improves",
                "Seeing some warning signs in the charts",
            ],
            "neutral": [
                "Holding steady, watching the market closely",
                "Mixed signals today, staying patient",
                "Waiting for better entry points",
                "No major moves planned for now",
                "Keeping powder dry for opportunities",
            ]
        }
        
        for agent in posters:
            # Sentiment based on recent performance
            if agent.pnl_percent > 5:
                sentiment = "bullish"
            elif agent.pnl_percent < -5:
                sentiment = "bearish"
            else:
                sentiment = "neutral"
            
            message = self._random.choice(message_templates[sentiment])
            
            self.state.forum_messages.append(ForumMessage(
                day=self.state.current_day,
                agent_id=agent.id,
                agent_name=agent.name,
                message=message,
                sentiment=sentiment
            ))
    
    def pause(self):
        """Pause the simulation."""
        if self.state.status == "RUNNING":
            self.state.status = "PAUSED"
        return self.state
    
    def resume(self):
        """Resume the simulation."""
        if self.state.status == "PAUSED":
            self.state.status = "RUNNING"
        return self.state
    
    def reset(self):
        """Reset the simulation."""
        self.state = SimulationState()
        return self.state
    
    def get_state(self) -> SimulationState:
        """Get the current simulation state."""
        return self.state
    
    def get_agent(self, agent_id: int) -> Optional[AgentState]:
        """Get a specific agent by ID."""
        for agent in self.state.agents:
            if agent.id == agent_id:
                return agent
        return None
    
    def get_price_history_df(self):
        """Get price history as a format suitable for charts."""
        if not self.state.stock_a or not self.state.stock_b:
            return None
        
        # Get unique days
        days = sorted(set(p["day"] for p in self.state.stock_a.price_history))
        
        # Get end-of-day prices
        price_a = []
        price_b = []
        
        for day in days:
            day_prices_a = [p["price"] for p in self.state.stock_a.price_history if p["day"] == day]
            day_prices_b = [p["price"] for p in self.state.stock_b.price_history if p["day"] == day]
            
            price_a.append(day_prices_a[-1] if day_prices_a else None)
            price_b.append(day_prices_b[-1] if day_prices_b else None)
        
        return {
            "days": days,
            "stock_a": price_a,
            "stock_b": price_b
        }
    
    def get_strategy_performance(self):
        """Get performance breakdown by strategy type."""
        strategies = {}
        
        for agent in self.state.agents:
            if agent.character not in strategies:
                strategies[agent.character] = {
                    "agents": [],
                    "total_pnl": 0,
                    "avg_pnl": 0,
                    "count": 0
                }
            
            strategies[agent.character]["agents"].append(agent)
            strategies[agent.character]["total_pnl"] += agent.pnl_percent
            strategies[agent.character]["count"] += 1
        
        for strategy in strategies.values():
            if strategy["count"] > 0:
                strategy["avg_pnl"] = strategy["total_pnl"] / strategy["count"]
        
        return strategies
    
    def get_today_events(self) -> List[MarketEvent]:
        """Get events for the current day."""
        return [e for e in self.state.events if e.day == self.state.current_day]
    
    def get_recent_messages(self, count: int = 10) -> List[ForumMessage]:
        """Get the most recent forum messages."""
        return self.state.forum_messages[-count:]


# ===============================
# SINGLETON INSTANCE
# ===============================

_engine_instance: Optional[SimulationEngine] = None

def get_engine() -> SimulationEngine:
    """Get or create the simulation engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SimulationEngine()
    return _engine_instance

def reset_engine() -> SimulationEngine:
    """Reset the simulation engine."""
    global _engine_instance
    _engine_instance = SimulationEngine()
    return _engine_instance
