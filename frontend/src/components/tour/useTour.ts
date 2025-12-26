/**
 * Tour Hook
 *
 * React hook for controlling the guided tour.
 * Manages tour state, navigation, auto-advance, and persistence.
 *
 * Features:
 * - Auto-advance with configurable duration per step
 * - Pause/resume capability (Space key)
 * - Route navigation between steps
 * - Keyboard navigation (arrows, escape)
 */

import { useCallback, useEffect, useState, useRef } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import { DEMO_TOUR_STEPS, type TourStep } from "./tourSteps";

// =============================================================================
// TYPES
// =============================================================================

export interface TourState {
  /** Whether the tour is currently active */
  isActive: boolean;
  /** Current step index (0-based) */
  currentStepIndex: number;
  /** Current step data */
  currentStep: TourStep | null;
  /** Total number of steps */
  totalSteps: number;
  /** Whether tour has been completed this session */
  hasCompleted: boolean;
  /** Whether auto-advance is paused */
  isPaused: boolean;
  /** Time remaining on current step (ms) */
  timeRemaining: number;
  /** Total duration of current step (ms) */
  stepDuration: number;
}

export interface TourActions {
  /** Start the tour from the beginning */
  startTour: () => void;
  /** End the tour (skip or complete) */
  endTour: () => void;
  /** Go to next step */
  nextStep: () => void;
  /** Go to previous step */
  prevStep: () => void;
  /** Go to a specific step by index */
  goToStep: (index: number) => void;
  /** Toggle pause state */
  togglePause: () => void;
  /** Check if we're on the first step */
  isFirstStep: boolean;
  /** Check if we're on the last step */
  isLastStep: boolean;
}

export type UseTourReturn = TourState & TourActions;

// =============================================================================
// CONSTANTS
// =============================================================================

const STORAGE_KEY = "braidmgr-demo-tour-completed";
const DEFAULT_STEP_DURATION = 6000; // 6 seconds
const TICK_INTERVAL = 100; // Update progress every 100ms

// =============================================================================
// HOOK
// =============================================================================

export function useTour(): UseTourReturn {
  const navigate = useNavigate();
  const location = useLocation();

  // Tour active state
  const [isActive, setIsActive] = useState(false);

  // Current step index
  const [currentStepIndex, setCurrentStepIndex] = useState(0);

  // Auto-advance state
  const [isPaused, setIsPaused] = useState(false);
  const [timeRemaining, setTimeRemaining] = useState(0);

  // Completion tracking
  const [hasCompleted, setHasCompleted] = useState(() => {
    if (typeof window === "undefined") return false;
    return localStorage.getItem(STORAGE_KEY) === "true";
  });

  // Track if we've navigated for current step
  const hasNavigatedRef = useRef(false);

  // Derived values
  const totalSteps = DEMO_TOUR_STEPS.length;
  const currentStep = isActive ? (DEMO_TOUR_STEPS[currentStepIndex] ?? null) : null;
  const isFirstStep = currentStepIndex === 0;
  const isLastStep = currentStepIndex === totalSteps - 1;
  const stepDuration = currentStep?.duration ?? DEFAULT_STEP_DURATION;

  // Start tour
  const startTour = useCallback(() => {
    setCurrentStepIndex(0);
    setIsActive(true);
    setIsPaused(false);
    hasNavigatedRef.current = false;
  }, []);

  // End tour
  const endTour = useCallback(() => {
    setIsActive(false);
    setIsPaused(false);
    if (currentStepIndex === totalSteps - 1) {
      setHasCompleted(true);
      localStorage.setItem(STORAGE_KEY, "true");
    }
  }, [currentStepIndex, totalSteps]);

  // Next step
  const nextStep = useCallback(() => {
    if (currentStepIndex < totalSteps - 1) {
      setCurrentStepIndex((prev) => prev + 1);
      hasNavigatedRef.current = false;
    } else {
      endTour();
    }
  }, [currentStepIndex, totalSteps, endTour]);

  // Previous step
  const prevStep = useCallback(() => {
    if (currentStepIndex > 0) {
      setCurrentStepIndex((prev) => prev - 1);
      hasNavigatedRef.current = false;
    }
  }, [currentStepIndex]);

  // Go to specific step
  const goToStep = useCallback(
    (index: number) => {
      if (index >= 0 && index < totalSteps) {
        setCurrentStepIndex(index);
        hasNavigatedRef.current = false;
      }
    },
    [totalSteps]
  );

  // Toggle pause
  const togglePause = useCallback(() => {
    setIsPaused((prev) => !prev);
  }, []);

  // Handle route navigation for steps
  useEffect(() => {
    if (!isActive || !currentStep?.route || hasNavigatedRef.current) return;

    // Check if we need to navigate
    if (location.pathname !== currentStep.route) {
      hasNavigatedRef.current = true;
      navigate(currentStep.route);
    }
  }, [isActive, currentStep, location.pathname, navigate]);

  // Auto-advance timer
  useEffect(() => {
    if (!isActive || isPaused) return;

    // Reset time when step changes
    setTimeRemaining(stepDuration);

    const interval = setInterval(() => {
      setTimeRemaining((prev) => {
        if (prev <= TICK_INTERVAL) {
          // Time's up - advance to next step
          nextStep();
          return stepDuration;
        }
        return prev - TICK_INTERVAL;
      });
    }, TICK_INTERVAL);

    return () => clearInterval(interval);
  }, [isActive, isPaused, currentStepIndex, stepDuration, nextStep]);

  // Handle keyboard navigation
  useEffect(() => {
    if (!isActive) return;

    const handleKeyDown = (e: KeyboardEvent) => {
      switch (e.key) {
        case "ArrowRight":
        case "Enter":
          e.preventDefault();
          nextStep();
          break;
        case "ArrowLeft":
          e.preventDefault();
          prevStep();
          break;
        case " ": // Space bar
          e.preventDefault();
          togglePause();
          break;
        case "Escape":
          e.preventDefault();
          endTour();
          break;
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [isActive, nextStep, prevStep, togglePause, endTour]);

  return {
    // State
    isActive,
    currentStepIndex,
    currentStep,
    totalSteps,
    hasCompleted,
    isPaused,
    timeRemaining,
    stepDuration,
    // Actions
    startTour,
    endTour,
    nextStep,
    prevStep,
    goToStep,
    togglePause,
    isFirstStep,
    isLastStep,
  };
}
