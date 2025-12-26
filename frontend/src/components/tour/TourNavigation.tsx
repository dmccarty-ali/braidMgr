/**
 * Tour Navigation
 *
 * Navigation controls for the guided tour.
 * Shows progress bar, step counter, pause/play, and prev/next buttons.
 */

import { useTourContext } from "./TourProvider";

// =============================================================================
// COMPONENT
// =============================================================================

export function TourNavigation() {
  const {
    currentStepIndex,
    totalSteps,
    nextStep,
    prevStep,
    endTour,
    togglePause,
    isFirstStep,
    isLastStep,
    isPaused,
    timeRemaining,
    stepDuration,
  } = useTourContext();

  // Calculate progress percentage
  const progressPercent = ((stepDuration - timeRemaining) / stepDuration) * 100;

  return (
    <div className="space-y-3">
      {/* Progress bar */}
      <div className="relative h-1 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="absolute inset-y-0 left-0 bg-blue-600 transition-all duration-100 ease-linear"
          style={{ width: `${progressPercent}%` }}
        />
      </div>

      <div className="flex items-center justify-between">
        {/* Left side: Step counter and pause button */}
        <div className="flex items-center gap-3">
          <span className="text-sm text-gray-500">
            Step {currentStepIndex + 1} of {totalSteps}
          </span>

          {/* Pause/Play button */}
          <button
            onClick={togglePause}
            className="flex items-center gap-1 px-2 py-1 text-sm text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
            title={isPaused ? "Resume (Space)" : "Pause (Space)"}
          >
            {isPaused ? (
              <>
                <PlayIcon />
                <span>Play</span>
              </>
            ) : (
              <>
                <PauseIcon />
                <span>Pause</span>
              </>
            )}
          </button>
        </div>

        {/* Right side: Navigation buttons */}
        <div className="flex gap-2">
          {/* Skip button */}
          <button
            onClick={endTour}
            className="px-3 py-1.5 text-sm text-gray-500 hover:text-gray-700 transition-colors"
          >
            Skip
          </button>

          {/* Previous button */}
          {!isFirstStep && (
            <button
              onClick={prevStep}
              className="px-4 py-1.5 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50 transition-colors"
            >
              Previous
            </button>
          )}

          {/* Next / Finish button */}
          <button
            onClick={nextStep}
            className="px-4 py-1.5 text-sm font-medium text-white bg-blue-600 rounded-md hover:bg-blue-700 transition-colors"
          >
            {isLastStep ? "Finish" : "Next"}
          </button>
        </div>
      </div>
    </div>
  );
}

// =============================================================================
// ICONS
// =============================================================================

function PauseIcon() {
  return (
    <svg
      className="w-4 h-4"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M18 10a8 8 0 11-16 0 8 8 0 0116 0zM7 8a1 1 0 012 0v4a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v4a1 1 0 102 0V8a1 1 0 00-1-1z"
        clipRule="evenodd"
      />
    </svg>
  );
}

function PlayIcon() {
  return (
    <svg
      className="w-4 h-4"
      fill="currentColor"
      viewBox="0 0 20 20"
    >
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z"
        clipRule="evenodd"
      />
    </svg>
  );
}
