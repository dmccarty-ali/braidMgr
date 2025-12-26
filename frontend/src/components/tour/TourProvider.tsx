/**
 * Tour Provider
 *
 * React context provider for the guided tour.
 * Wraps the app and provides tour state to all components.
 */

import { createContext, useContext, type ReactNode } from "react";
import { useTour, type UseTourReturn } from "./useTour";

// =============================================================================
// CONTEXT
// =============================================================================

const TourContext = createContext<UseTourReturn | null>(null);

// =============================================================================
// PROVIDER
// =============================================================================

export interface TourProviderProps {
  children: ReactNode;
}

export function TourProvider({ children }: TourProviderProps) {
  const tour = useTour();

  return <TourContext.Provider value={tour}>{children}</TourContext.Provider>;
}

// =============================================================================
// HOOK
// =============================================================================

/**
 * Use the tour context.
 * Must be used within a TourProvider.
 */
export function useTourContext(): UseTourReturn {
  const context = useContext(TourContext);

  if (!context) {
    throw new Error("useTourContext must be used within a TourProvider");
  }

  return context;
}
