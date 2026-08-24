import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.chart_service import BirthData, build
from stellium.visualization.vedic.north_indian import NorthIndianRenderer
from stellium.visualization.vedic.south_indian import SouthIndianRenderer
from app.astro.panchang import SIGNS

class VargaChartWrapper:
    def __init__(self, original_chart, division: str):
        self.metadata = getattr(original_chart.chart, "metadata", {})
        self.datetime = getattr(original_chart.chart, "datetime", None)
        self.location = getattr(original_chart.chart, "location", None)
        
        # Compute the varga signs
        from app.astro.vargas import divisional_chart
        v_data = divisional_chart(original_chart, division)
        lagna_sign = v_data["lagna"]["sign"] if isinstance(v_data["lagna"], dict) else v_data["lagna"]
        
        lagna_idx = SIGNS.index(lagna_sign)
        
        class HouseMock:
            cusps = [lagna_idx * 30.0] * 12
        self._houses = HouseMock()
        
        self._planets = []
        class PlanetMock:
            def __init__(self, name, longitude, speed_longitude):
                self.name = name
                self.longitude = longitude
                self.speed_longitude = speed_longitude
                
            def __repr__(self):
                return f"{self.name}@{self.longitude}"
                
        # Import VedicPlanetInfo from stellium visualization if needed, but the renderer uses attributes
        # Let's see if NorthIndianRenderer._get_planets_by_sign uses pos.speed_longitude
        for pl_name, pl_info in v_data["positions"].items():
            if pl_name == "Lagna":
                continue
            pl_sign = pl_info["sign"]
            pl_idx = SIGNS.index(pl_sign)
            
            orig_pl = original_chart.chart.get_object(pl_name)
            speed = -1.0 if (orig_pl and orig_pl.speed_longitude and orig_pl.speed_longitude < 0) else 1.0
            
            self._planets.append(PlanetMock(pl_name, pl_idx * 30.0 + 15.0, speed))
            
    def get_houses(self):
        return self._houses
        
    def get_planets(self):
        return self._planets
        
    def get_object(self, name):
        for p in self._planets:
            if p.name == name:
                return p
        return None

def test_varga():
    bd = BirthData(
        name="Sanskruti", date="1999-08-14", time="14:07",
        latitude=18.5204, longitude=73.8567, timezone="Asia/Kolkata",
        place="Pune", zodiac="sidereal", ayanamsa="lahiri", house_system="Whole Sign"
    )
    s = build(bd)
    print("Original chart loaded.")
    
    # Wrap D9
    wrapper = VargaChartWrapper(s, "D9")
    print("D9 wrapped. Planets:", wrapper.get_planets())
    
    # Draw North Indian
    renderer = NorthIndianRenderer(size=520, theme="classic")
    svg_data = renderer.render(wrapper)
    print("D9 North Indian SVG rendered. Length:", len(svg_data))
    
    # Draw South Indian
    renderer2 = SouthIndianRenderer(size=520, theme="classic")
    svg_data2 = renderer2.render(wrapper)
    print("D9 South Indian SVG rendered. Length:", len(svg_data2))

if __name__ == "__main__":
    test_varga()
