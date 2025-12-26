/**
 * Tour Overlay
 *
 * Renders the spotlight overlay and tooltip for the current tour step.
 * Uses CSS clip-path for the spotlight "hole" effect.
 */

import { useEffect, useState, useRef } from "react";
import { useTourContext } from "./TourProvider";
import { TourNavigation } from "./TourNavigation";
import type { TourStep } from "./tourSteps";

// =============================================================================
// TYPES
// =============================================================================

interface TargetRect {
  top: number;
  left: number;
  width: number;
  height: number;
}

// =============================================================================
// COMPONENT
// =============================================================================

export function TourOverlay() {
  const { isActive, currentStep } = useTourContext();
  const [targetRect, setTargetRect] = useState<TargetRect | null>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  // Find and track target element position
  useEffect(() => {
    if (!isActive || !currentStep?.target) {
      setTargetRect(null);
      return;
    }

    const findTarget = () => {
      const target = document.querySelector(currentStep.target as string);
      if (target) {
        const rect = target.getBoundingClientRect();
        const padding = currentStep.spotlightPadding ?? 8;
        setTargetRect({
          top: rect.top - padding + window.scrollY,
          left: rect.left - padding,
          width: rect.width + padding * 2,
          height: rect.height + padding * 2,
        });
      } else if (currentStep.waitForTarget) {
        // Retry if element not found yet
        setTimeout(findTarget, 100);
      } else {
        setTargetRect(null);
      }
    };

    findTarget();

    // Update on resize/scroll
    window.addEventListener("resize", findTarget);
    window.addEventListener("scroll", findTarget);

    return () => {
      window.removeEventListener("resize", findTarget);
      window.removeEventListener("scroll", findTarget);
    };
  }, [isActive, currentStep]);

  // Don't render if tour is not active
  if (!isActive || !currentStep) {
    return null;
  }

  // Calculate tooltip position
  const tooltipPosition = calculateTooltipPosition(
    currentStep,
    targetRect,
    tooltipRef.current
  );

  return (
    <>
      {/* Backdrop with spotlight hole */}
      <div
        className="fixed inset-0 z-[9998] pointer-events-auto"
        style={{
          backgroundColor: "rgba(0, 0, 0, 0.75)",
          clipPath: targetRect
            ? `polygon(
                0% 0%,
                0% 100%,
                ${targetRect.left}px 100%,
                ${targetRect.left}px ${targetRect.top}px,
                ${targetRect.left + targetRect.width}px ${targetRect.top}px,
                ${targetRect.left + targetRect.width}px ${targetRect.top + targetRect.height}px,
                ${targetRect.left}px ${targetRect.top + targetRect.height}px,
                ${targetRect.left}px 100%,
                100% 100%,
                100% 0%
              )`
            : undefined,
        }}
      />

      {/* Tooltip */}
      <div
        ref={tooltipRef}
        className="fixed z-[9999] w-[400px] max-w-[90vw]"
        style={{
          top: tooltipPosition.top,
          left: tooltipPosition.left,
          transform: tooltipPosition.transform,
        }}
      >
        <div className="bg-white rounded-lg shadow-2xl border border-gray-200 overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-blue-700 px-5 py-4">
            <h3 className="text-lg font-semibold text-white">
              {currentStep.title}
            </h3>
          </div>

          {/* Content */}
          <div className="px-5 py-4">
            <div className="prose prose-sm max-w-none text-gray-700">
              <TourContent content={currentStep.content} />
            </div>

            {/* Talking point badge */}
            {currentStep.talkingPoint && (
              <div className="mt-4 p-3 bg-blue-50 rounded-lg border border-blue-100">
                <p className="text-sm text-blue-800 font-medium flex items-center">
                  <span className="text-blue-500 mr-2">&#128161;</span>
                  {currentStep.talkingPoint}
                </p>
              </div>
            )}
          </div>

          {/* Navigation */}
          <div className="px-5 py-4 bg-gray-50 border-t border-gray-100">
            <TourNavigation />
          </div>
        </div>

        {/* Arrow pointing to target */}
        {targetRect && currentStep.placement !== "center" && (
          <TooltipArrow placement={currentStep.placement} />
        )}
      </div>
    </>
  );
}

// =============================================================================
// HELPER COMPONENTS
// =============================================================================

/**
 * Render markdown-like content
 */
function TourContent({ content }: { content: string }) {
  const lines = content.split("\n");

  return (
    <div className="space-y-2">
      {lines.map((line, i) => {
        // Empty line
        if (!line.trim()) {
          return <div key={i} className="h-2" />;
        }

        // Bold text (**text**)
        let processedLine = line.replace(
          /\*\*([^*]+)\*\*/g,
          '<strong class="font-semibold text-gray-900">$1</strong>'
        );

        // List items (- item)
        if (processedLine.trim().startsWith("- ")) {
          return (
            <div key={i} className="flex items-start">
              <span className="text-blue-500 mr-2 mt-0.5">&#8226;</span>
              <span
                dangerouslySetInnerHTML={{
                  __html: processedLine.replace("- ", ""),
                }}
              />
            </div>
          );
        }

        // Numbered items (1. item)
        const numberedMatch = processedLine.match(/^(\d+)\.\s+(.+)/);
        if (numberedMatch && numberedMatch[1] && numberedMatch[2]) {
          return (
            <div key={i} className="flex items-start">
              <span className="text-blue-500 mr-2 font-medium min-w-[1.5rem]">
                {numberedMatch[1]}.
              </span>
              <span
                dangerouslySetInnerHTML={{
                  __html: numberedMatch[2],
                }}
              />
            </div>
          );
        }

        // Regular paragraph
        return (
          <p
            key={i}
            dangerouslySetInnerHTML={{ __html: processedLine }}
          />
        );
      })}
    </div>
  );
}

/**
 * Arrow pointing from tooltip to target
 */
function TooltipArrow({ placement }: { placement: string }) {
  const arrowClasses = {
    top: "bottom-full left-1/2 -translate-x-1/2 border-b-white border-l-transparent border-r-transparent border-t-transparent",
    bottom: "top-full left-1/2 -translate-x-1/2 border-t-white border-l-transparent border-r-transparent border-b-transparent",
    left: "right-full top-1/2 -translate-y-1/2 border-r-white border-t-transparent border-b-transparent border-l-transparent",
    right: "left-full top-1/2 -translate-y-1/2 border-l-white border-t-transparent border-b-transparent border-r-transparent",
  };

  const className = arrowClasses[placement as keyof typeof arrowClasses] || "";

  return (
    <div
      className={`absolute w-0 h-0 border-8 ${className}`}
      style={{ filter: "drop-shadow(0 1px 2px rgba(0,0,0,0.1))" }}
    />
  );
}

// =============================================================================
// HELPERS
// =============================================================================

/**
 * Calculate tooltip position based on target and placement
 */
function calculateTooltipPosition(
  step: TourStep,
  targetRect: TargetRect | null,
  tooltip: HTMLDivElement | null
): { top: string; left: string; transform: string } {
  // Center modal (no target)
  if (!targetRect || step.placement === "center") {
    return {
      top: "50%",
      left: "50%",
      transform: "translate(-50%, -50%)",
    };
  }

  const tooltipHeight = tooltip?.offsetHeight || 300;
  const tooltipWidth = tooltip?.offsetWidth || 400;
  const margin = 16;

  switch (step.placement) {
    case "top":
      return {
        top: `${targetRect.top - tooltipHeight - margin}px`,
        left: `${targetRect.left + targetRect.width / 2}px`,
        transform: "translateX(-50%)",
      };
    case "bottom":
      return {
        top: `${targetRect.top + targetRect.height + margin}px`,
        left: `${targetRect.left + targetRect.width / 2}px`,
        transform: "translateX(-50%)",
      };
    case "left":
      return {
        top: `${targetRect.top + targetRect.height / 2}px`,
        left: `${targetRect.left - tooltipWidth - margin}px`,
        transform: "translateY(-50%)",
      };
    case "right":
      return {
        top: `${targetRect.top + targetRect.height / 2}px`,
        left: `${targetRect.left + targetRect.width + margin}px`,
        transform: "translateY(-50%)",
      };
    default:
      return {
        top: "50%",
        left: "50%",
        transform: "translate(-50%, -50%)",
      };
  }
}
