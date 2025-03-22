from typing import Dict, List, Optional, Union, Any
import pandas as pd

from app.models.prediction import (
    BasicFishPredictionModel,
    AdvancedFishPredictionModel,
    WaterQualityModel
)
from app.models.schemas import (
    BasicFishPredictionRequest,
    AdvancedFishPredictionRequest,
    FishSpeciesInfo
)
from app.core.logging import logger


class PredictionService:
    """Service for making predictions using trained models."""
    
    def __init__(self):
        """Initialize the prediction service with model instances."""
        self.basic_model = BasicFishPredictionModel()
        self.advanced_model = AdvancedFishPredictionModel()
        self.water_quality_model = WaterQualityModel()
        
        # Fish species information database
        self.fish_species_info = self._initialize_species_info()
    
    def _initialize_species_info(self) -> Dict[str, FishSpeciesInfo]:
        """Initialize information about fish species."""
        # This could be loaded from a database or external file
        species_info = {
            "Tilapia": FishSpeciesInfo(
                name="Tilapia",
                scientific_name="Oreochromis niloticus",
                ideal_ph_range=[6.5, 8.0],
                ideal_temperature_range=[25.0, 30.0],
                ideal_turbidity_range=[30.0, 80.0],
                description="Tilapia is a hardy fish that can tolerate a wide range of water conditions. It's popular in aquaculture due to its fast growth rate and adaptability."
            ),
            "Catfish": FishSpeciesInfo(
                name="Catfish",
                scientific_name="Clarias gariepinus",
                ideal_ph_range=[6.0, 8.0],
                ideal_temperature_range=[24.0, 28.0],
                ideal_turbidity_range=[20.0, 60.0],
                description="Catfish are bottom-dwelling fish that can tolerate low oxygen levels and poor water quality. They are widely farmed for their high-quality meat."
            ),
            "Carp": FishSpeciesInfo(
                name="Carp",
                scientific_name="Cyprinus carpio",
                ideal_ph_range=[6.5, 9.0],
                ideal_temperature_range=[20.0, 28.0],
                ideal_turbidity_range=[30.0, 70.0],
                description="Carp is one of the most widely cultivated freshwater fish. It's tolerant of poor water conditions and can survive in water with low oxygen levels."
            ),
            "Salmon": FishSpeciesInfo(
                name="Salmon",
                scientific_name="Salmo salar",
                ideal_ph_range=[6.5, 8.0],
                ideal_temperature_range=[10.0, 16.0],
                ideal_turbidity_range=[5.0, 20.0],
                description="Salmon require clean, cold, oxygen-rich water. They are sensitive to water quality changes and need pristine conditions for optimal growth."
            ),
            "Trout": FishSpeciesInfo(
                name="Trout",
                scientific_name="Oncorhynchus mykiss",
                ideal_ph_range=[6.5, 8.0],
                ideal_temperature_range=[12.0, 18.0],
                ideal_turbidity_range=[5.0, 25.0],
                description="Trout are cold-water fish that require high-quality water with good oxygen levels. They're sensitive to pollution and temperature changes."
            ),
            "Shrimp": FishSpeciesInfo(
                name="Shrimp",
                scientific_name="Litopenaeus vannamei",
                ideal_ph_range=[7.0, 8.5],
                ideal_temperature_range=[26.0, 32.0],
                ideal_turbidity_range=[30.0, 60.0],
                description="Shrimp are highly sensitive to water quality parameters. They require stable conditions with careful management of ammonia and nitrite levels."
            ),
            "Goldfish": FishSpeciesInfo(
                name="Goldfish",
                scientific_name="Carassius auratus",
                ideal_ph_range=[6.0, 8.0],
                ideal_temperature_range=[20.0, 25.0],
                ideal_turbidity_range=[20.0, 50.0],
                description="Goldfish are hardy freshwater fish that can adapt to various water conditions. They're popular ornamental fish and can tolerate cooler temperatures."
            )
        }
        return species_info
    
    def predict_basic(self, data: BasicFishPredictionRequest) -> Dict[str, Any]:
        """Make prediction using the basic model."""
        logger.info(f"Making basic prediction with data: {data}")
        
        input_data = {
            'ph': data.ph,
            'temperature': data.temperature,
            'turbidity': data.turbidity
        }
        
        # Try to use the model first
        try:
            # Try model-based prediction
            prediction_result = self.basic_model.predict(input_data)
            predicted_species = prediction_result['predicted_species']
            confidence = prediction_result['confidence']
        except Exception as e:
            # Fallback to rule-based prediction if model fails
            logger.warning(f"Model prediction failed, using rule-based fallback: {e}")
            # Simple rule-based prediction
            ph = data.ph
            temperature = data.temperature
            turbidity = data.turbidity
            
            # Default values
            predicted_species = "Tilapia"  # Default
            confidence = 0.7
            
            # Simple rules for species prediction
            if 6.5 <= ph <= 7.5 and 25 <= temperature <= 30 and 30 <= turbidity <= 60:
                predicted_species = "Tilapia"
                confidence = 0.85
            elif 6.0 <= ph <= 7.0 and 24 <= temperature <= 28 and 20 <= turbidity <= 50:
                predicted_species = "Catfish"
                confidence = 0.80
            elif 6.5 <= ph <= 8.0 and 20 <= temperature <= 26 and 30 <= turbidity <= 70:
                predicted_species = "Carp"
                confidence = 0.75
            elif 6.5 <= ph <= 8.0 and 10 <= temperature <= 18 and 5 <= turbidity <= 25:
                predicted_species = "Trout"
                confidence = 0.90
        
        # Get water quality score using a simplified calculation
        water_quality_score = 0
        if 6.5 <= data.ph <= 8.5:
            water_quality_score += 3
        elif 6.0 <= data.ph <= 9.0:
            water_quality_score += 2
        else:
            water_quality_score += 1
            
        if 22 <= data.temperature <= 30:
            water_quality_score += 3
        elif 18 <= data.temperature <= 32:
            water_quality_score += 2
        else:
            water_quality_score += 1
            
        if 30 <= data.turbidity <= 80:
            water_quality_score += 3
        elif 20 <= data.turbidity <= 100:
            water_quality_score += 2
        else:
            water_quality_score += 1
            
        # Normalize to 0-10 scale
        water_quality_score = (water_quality_score / 9) * 10
        
        # Analyze parameters
        parameter_analysis = self._analyze_parameters_basic(input_data)
        
        # Get suitable species
        suitable_species = self._get_suitable_species_basic(input_data)
        
        result = {
            'predicted_species': predicted_species,
            'confidence': confidence,
            'water_quality_score': water_quality_score,
            'parameter_analysis': parameter_analysis,
            'suitable_species': [
                self.fish_species_info.get(species, FishSpeciesInfo(name=species))
                for species in suitable_species
            ]
        }
        
        return result
    
    def predict_advanced(self, data: AdvancedFishPredictionRequest) -> Dict[str, Any]:
        """Make prediction using the advanced model."""
        logger.info(f"Making advanced prediction with data")
        
        input_data = {
            'temperature': data.temperature,
            'turbidity': data.turbidity,
            'dissolved_oxygen': data.dissolved_oxygen,
            'bod': data.bod,
            'co2': data.co2,
            'ph': data.ph,
            'alkalinity': data.alkalinity,
            'hardness': data.hardness,
            'calcium': data.calcium,
            'ammonia': data.ammonia,
            'nitrite': data.nitrite,
            'phosphorus': data.phosphorus,
            'h2s': data.h2s,
            'plankton': data.plankton
        }
        
        # Get prediction from model
        try:
            prediction_result = self.advanced_model.predict(input_data)
            predicted_species = prediction_result['predicted_species']
            confidence = prediction_result['confidence']
            
            # Get water quality score
            water_quality_score = None
            try:
                if self.water_quality_model.model:
                    water_quality_score = self.water_quality_model.predict(input_data)
            except Exception as e:
                logger.warning(f"Error getting water quality score: {e}")
                # Fallback calculation for water quality score
                water_quality_score = self._calculate_water_quality_score(input_data)
            
            # Analyze parameters
            parameter_analysis = self._analyze_parameters_advanced(input_data)
            
            # Get suitable species
            suitable_species = self._get_suitable_species_advanced(input_data)
            
            result = {
                'predicted_species': predicted_species,
                'confidence': confidence,
                'water_quality_score': water_quality_score,
                'parameter_analysis': parameter_analysis,
                'suitable_species': [
                    self.fish_species_info.get(species, FishSpeciesInfo(name=species))
                    for species in suitable_species
                ]
            }
            
            return result
        
        except Exception as e:
            logger.error(f"Error making advanced prediction: {e}")
            # Fallback to simpler prediction logic
            try:
                # Use a simplified approach with the basic parameters
                basic_data = BasicFishPredictionRequest(
                    ph=data.ph,
                    temperature=data.temperature,
                    turbidity=data.turbidity
                )
                return self.predict_basic(basic_data)
            except Exception as inner_e:
                logger.error(f"Fallback prediction also failed: {inner_e}")
                raise
    
    def _calculate_water_quality_score(self, data: Dict[str, float]) -> float:
        """Calculate water quality score based on parameter values."""
        score = 0
        total_weight = 0
        
        # pH
        if 'ph' in data:
            ph = data['ph']
            weight = 1.5
            total_weight += weight
            if 6.5 <= ph <= 8.5:
                score += weight * 1.0
            elif 6.0 <= ph <= 9.0:
                score += weight * 0.7
            else:
                score += weight * 0.3
        
        # Temperature
        if 'temperature' in data:
            temp = data['temperature']
            weight = 1.0
            total_weight += weight
            if 20 <= temp <= 30:
                score += weight * 1.0
            elif 15 <= temp <= 35:
                score += weight * 0.7
            else:
                score += weight * 0.3
        
        # Dissolved Oxygen
        if 'dissolved_oxygen' in data:
            do = data['dissolved_oxygen']
            weight = 2.0
            total_weight += weight
            if do >= 6.0:
                score += weight * 1.0
            elif do >= 4.0:
                score += weight * 0.7
            else:
                score += weight * 0.3
        
        # Add more parameters as needed
        
        # Calculate final score (0-10)
        return (score / total_weight) * 10 if total_weight > 0 else 5.0
    
    def _analyze_parameters_basic(self, data: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Analyze basic water parameters and provide status and recommendations."""
        analysis = {}
        
        # pH analysis
        ph = data.get('ph')
        if ph:
            ph_status = 'optimal' if 6.5 <= ph <= 8.5 else 'suboptimal'
            ph_recommendation = None
            if ph < 6.5:
                ph_recommendation = "Consider adding limestone or calcium carbonate to increase pH"
            elif ph > 8.5:
                ph_recommendation = "Consider adding natural acids like peat or driftwood to decrease pH"
            
            analysis['ph'] = {
                'value': ph,
                'status': ph_status,
                'recommendation': ph_recommendation
            }
        
        # Temperature analysis
        temp = data.get('temperature')
        if temp:
            temp_status = 'optimal' if 20 <= temp <= 30 else 'suboptimal'
            temp_recommendation = None
            if temp < 20:
                temp_recommendation = "Consider using heaters to increase water temperature"
            elif temp > 30:
                temp_recommendation = "Consider cooling methods like shade or water exchange"
            
            analysis['temperature'] = {
                'value': temp,
                'status': temp_status,
                'recommendation': temp_recommendation
            }
        
        # Turbidity analysis
        turbidity = data.get('turbidity')
        if turbidity:
            turbidity_status = 'optimal' if 30 <= turbidity <= 80 else 'suboptimal'
            turbidity_recommendation = None
            if turbidity < 30:
                turbidity_recommendation = "Water is very clear, which may indicate low productivity"
            elif turbidity > 80:
                turbidity_recommendation = "Water is too cloudy, consider filtration or water exchange"
            
            analysis['turbidity'] = {
                'value': turbidity,
                'status': turbidity_status,
                'recommendation': turbidity_recommendation
            }
        
        return analysis
    
    def _analyze_parameters_advanced(self, data: Dict[str, float]) -> Dict[str, Dict[str, Any]]:
        """Analyze advanced water parameters and provide status and recommendations."""
        # Start with basic analysis
        analysis = self._analyze_parameters_basic(data)
        
        # Add analysis for additional parameters
        
        # Dissolved oxygen
        do = data.get('dissolved_oxygen')
        if do:
            do_status = 'optimal' if 5 <= do <= 9 else 'suboptimal'
            do_recommendation = None
            if do < 5:
                do_recommendation = "Low oxygen levels. Consider aeration or reducing fish density"
            elif do > 9:
                do_recommendation = "High oxygen levels, possibly due to excessive algae growth"
            
            analysis['dissolved_oxygen'] = {
                'value': do,
                'status': do_status,
                'recommendation': do_recommendation
            }
        
        # Ammonia
        ammonia = data.get('ammonia')
        if ammonia:
            ammonia_status = 'optimal' if ammonia < 0.1 else 'suboptimal'
            ammonia_recommendation = None
            if ammonia >= 0.1:
                ammonia_recommendation = "High ammonia levels. Reduce feeding and increase water exchange"
            
            analysis['ammonia'] = {
                'value': ammonia,
                'status': ammonia_status,
                'recommendation': ammonia_recommendation
            }
        
        # Nitrite
        nitrite = data.get('nitrite')
        if nitrite:
            nitrite_status = 'optimal' if nitrite < 0.05 else 'suboptimal'
            nitrite_recommendation = None
            if nitrite >= 0.05:
                nitrite_recommendation = "High nitrite levels. Check biofilter and reduce feeding"
            
            analysis['nitrite'] = {
                'value': nitrite,
                'status': nitrite_status,
                'recommendation': nitrite_recommendation
            }
        
        return analysis
    
    def _get_suitable_species_basic(self, data: Dict[str, float]) -> List[str]:
        """Determine suitable fish species based on basic water parameters."""
        ph = data.get('ph', 7.0)
        temperature = data.get('temperature', 25.0)
        turbidity = data.get('turbidity', 50.0)
        
        suitable_species = []
        
        for species_name, info in self.fish_species_info.items():
            ph_range = info.ideal_ph_range or [6.0, 8.5]
            temp_range = info.ideal_temperature_range or [18.0, 32.0]
            turbidity_range = info.ideal_turbidity_range or [20.0, 80.0]
            
            if (ph_range[0] <= ph <= ph_range[1] and
                temp_range[0] <= temperature <= temp_range[1] and
                turbidity_range[0] <= turbidity <= turbidity_range[1]):
                suitable_species.append(species_name)
        
        return suitable_species
    
    def _get_suitable_species_advanced(self, data: Dict[str, float]) -> List[str]:
        """Determine suitable fish species based on advanced water parameters."""
        # Start with basic parameters check
        suitable_from_basic = self._get_suitable_species_basic(data)
        
        # Additional filtering based on advanced parameters
        do = data.get('dissolved_oxygen', 6.0)
        ammonia = data.get('ammonia', 0.05)
        nitrite = data.get('nitrite', 0.01)
        
        suitable_species = []
        
        for species in suitable_from_basic:
            # Apply additional criteria based on species requirements
            if species == "Salmon" or species == "Trout":
                # Cold water species need high oxygen
                if do >= 7.0 and ammonia < 0.05 and nitrite < 0.01:
                    suitable_species.append(species)
            elif species == "Tilapia" or species == "Catfish" or species == "Carp":
                # More tolerant species
                if do >= 4.0:
                    suitable_species.append(species)
            else:
                # Default case
                if do >= 5.0 and ammonia < 0.1 and nitrite < 0.05:
                    suitable_species.append(species)
        
        return suitable_species