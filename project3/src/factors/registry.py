"""Factor provider registry for managing all factor providers."""

import logging
from typing import Dict, Set, Optional
from .base import FactorProvider

logger = logging.getLogger(__name__)


class FactorRegistry:
    """Registry for managing factor providers."""
    
    _instance: Optional['FactorRegistry'] = None
    
    def __new__(cls):
        """Singleton pattern - ensure only one registry instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the registry."""
        if self._initialized:
            return
        
        self._providers: Dict[str, FactorProvider] = {}
        self._initialized = True
        logger.debug("FactorRegistry initialized")
    
    def register(self, provider: FactorProvider) -> None:
        """
        Register a factor provider.
        
        Args:
            provider: FactorProvider instance to register
            
        Raises:
            ValueError: If provider name already exists
        """
        if provider.name in self._providers:
            raise ValueError(
                f"Provider with name '{provider.name}' already registered. "
                f"Use unregister() first or use a different name."
            )
        
        self._providers[provider.name] = provider
        logger.info(f"Registered factor provider: {provider.name}")
    
    def unregister(self, name: str) -> None:
        """
        Unregister a factor provider.
        
        Args:
            name: Name of provider to unregister
        """
        if name in self._providers:
            del self._providers[name]
            logger.info(f"Unregistered factor provider: {name}")
        else:
            logger.warning(f"Provider '{name}' not found in registry")
    
    def get_provider(self, name: str) -> Optional[FactorProvider]:
        """
        Get a provider by name.
        
        Args:
            name: Name of the provider
            
        Returns:
            FactorProvider instance or None if not found
        """
        return self._providers.get(name)
    
    def list_providers(self) -> list:
        """
        List all registered provider names.
        
        Returns:
            List of provider names
        """
        return list(self._providers.keys())
    
    def get_all_factors(self) -> Set[str]:
        """
        Get union of all factors from all registered providers.
        
        Returns:
            Set of all available factor names
        """
        all_factors = set()
        for provider in self._providers.values():
            all_factors.update(provider.get_available_factors())
        return all_factors
    
    def get_factors_by_provider(self, provider_name: str) -> Optional[Set[str]]:
        """
        Get factors available from a specific provider.
        
        Args:
            provider_name: Name of the provider
            
        Returns:
            Set of factor names or None if provider not found
        """
        provider = self.get_provider(provider_name)
        if provider:
            return provider.get_available_factors()
        return None
    
    def clear(self) -> None:
        """Clear all registered providers."""
        self._providers.clear()
        logger.info("Cleared all providers from registry")
    
    def __len__(self) -> int:
        """Return number of registered providers."""
        return len(self._providers)
    
    def __contains__(self, name: str) -> bool:
        """Check if a provider is registered."""
        return name in self._providers

