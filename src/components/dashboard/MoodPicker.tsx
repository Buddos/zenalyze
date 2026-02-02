import { useState } from "react";
import { cn } from "@/lib/utils";

const moods = [
  { emoji: "😊", label: "Happy", value: 5, gradient: "from-yellow-400 to-orange-400" },
  { emoji: "😌", label: "Calm", value: 4, gradient: "from-green-400 to-teal-400" },
  { emoji: "😐", label: "Neutral", value: 3, gradient: "from-gray-400 to-slate-400" },
  { emoji: "😔", label: "Sad", value: 2, gradient: "from-blue-400 to-indigo-400" },
  { emoji: "😰", label: "Anxious", value: 1, gradient: "from-orange-400 to-red-400" },
];

interface MoodPickerProps {
  onSelect: (mood: { emoji: string; label: string; value: number }) => void;
  selectedMood?: number;
}

const MoodPicker = ({ onSelect, selectedMood }: MoodPickerProps) => {
  return (
    <div className="flex items-center justify-center gap-4">
      {moods.map((mood) => (
        <button
          key={mood.value}
          onClick={() => onSelect(mood)}
          className={cn(
            "relative group flex flex-col items-center gap-2 p-4 rounded-2xl transition-all duration-300",
            selectedMood === mood.value
              ? "scale-110 shadow-lg"
              : "hover:scale-105 hover:shadow-md"
          )}
        >
          {/* Background gradient */}
          <div
            className={cn(
              "absolute inset-0 rounded-2xl bg-gradient-to-br opacity-20 transition-opacity",
              mood.gradient,
              selectedMood === mood.value ? "opacity-40" : "group-hover:opacity-30"
            )}
          />
          
          {/* Emoji */}
          <span className="relative text-5xl transition-transform duration-300 group-hover:scale-110">
            {mood.emoji}
          </span>
          
          {/* Label */}
          <span className={cn(
            "relative text-sm font-medium transition-colors",
            selectedMood === mood.value ? "text-foreground" : "text-muted-foreground"
          )}>
            {mood.label}
          </span>

          {/* Selection indicator */}
          {selectedMood === mood.value && (
            <div className={cn(
              "absolute -bottom-1 left-1/2 -translate-x-1/2 w-8 h-1 rounded-full bg-gradient-to-r",
              mood.gradient
            )} />
          )}
        </button>
      ))}
    </div>
  );
};

export default MoodPicker;
