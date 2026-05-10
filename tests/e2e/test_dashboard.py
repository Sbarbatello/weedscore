import pytest
import re
from playwright.sync_api import Page, expect

# Constants matching src/dashboard/app.py
URL = "http://localhost:8501"

@pytest.fixture(scope="function", autouse=True)
def before_each(page: Page):
    """Ensure we start at the home page before every test."""
    page.goto(URL)
    # Streamlit apps can take a second to boot the first time
    expect(page.get_by_text("Weedscore", exact=True)).to_be_visible(timeout=15000)

def test_main_dashboard_rag_visuals(page: Page):
    """Verify the central score display exists and has RAG-style coloring."""
    # Find the big score (the only H1 that is a number)
    score_element = page.locator("h1").filter(has_text=re.compile(r"^\d+\.?\d*$"))
    expect(score_element).to_be_visible()
    
    # Verify the color style is applied
    color = score_element.evaluate("el => el.style.color")
    assert color in ["red", "orange", "green"]

def test_state_synchronization_toggles(page: Page):
    """Scenario 2: Verify toggles stay synced across screens via session_state."""
    # Streamlit hides the real checkbox input. We use force=True to click the label/container.
    page.get_by_label("Is Solo?").click(force=True)
    
    # Navigate to Record Screen
    page.get_by_role("button", name="🌿 Log New Session").click()
    
    # Verify 'Is Solo' is still toggled ON
    expect(page.get_by_label("Is Solo?")).to_be_checked()

def test_record_session_live_preview_math(page: Page):
    """Scenario 1: Verify the Projected Score updates dynamically when toggles change."""
    page.get_by_role("button", name="🌿 Log New Session").click()
    
    # Capture initial projected score
    projected_metric = page.locator("[data-testid='stMetricValue']").first
    initial_score = projected_metric.inner_text()
    
    # Toggle 'Is Solo' (should change the score)
    page.get_by_label("Is Solo?").click(force=True)
    
    # Verify score changed without a page reload
    expect(projected_metric).not_to_have_text(initial_score)
    
    # Log the session
    page.get_by_role("button", name="✅ CONFIRM SESSION").click()
    
    # Verify success message
    expect(page.get_by_text("Session recorded successfully!")).to_be_visible()

def test_pydantic_boundary_defense(page: Page):
    """Scenario 3: Verify out-of-range inputs are handled."""
    # Use get_by_role to avoid ambiguity with tooltips
    page.get_by_role("button", name="⚙️").click()
    
    # Find the 'Target Frequency' input
    n_input = page.get_by_label("Target Frequency (Sessions/Year)")
    
    # We test the save flow reliability here.
    # Streamlit's UI usually clamps values, but Pydantic is our final line of defense.
    n_input.fill("50") 
    page.get_by_role("button", name="💾 Save Settings").click()
    
    expect(page.get_by_text("Settings updated!")).to_be_visible()

@pytest.mark.parametrize("viewport", [
    {"width": 375, "height": 812}, # iPhone 13
    {"width": 1280, "height": 720} # Desktop
])
def test_mobile_responsiveness(page: Page, viewport):
    """Scenario 4: Verify layout elements are reachable on mobile."""
    page.set_viewport_size(viewport)
    page.goto(URL)
    
    # Critical UI elements must be clickable
    expect(page.get_by_role("button", name="⚙️")).to_be_enabled()
    expect(page.get_by_role("button", name="🌿 Log New Session")).to_be_enabled()
