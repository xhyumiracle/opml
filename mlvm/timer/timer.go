// timer.go
package timer

import (
	"fmt"
	"time"
)

// fmt.Printf("[Warning] timer %s does not exist\n", name)

// Global map to hold timers
var timers = make(map[string]struct {
	start   time.Time
	elapsed time.Duration
	stopped bool
})

var ENABLE = true

// GetTimerNames returns a slice of all timer names
func GetTimerNames() []string {
	names := make([]string, 0, len(timers))
	for name := range timers {
		names = append(names, name)
	}
	return names
}

func ConvertUint(d time.Duration, unit string) (float64, bool) {
	conversionFactor := map[string]float64{
		"ns":  float64(time.Nanosecond),
		"us":  float64(time.Microsecond),
		"ms":  float64(time.Millisecond),
		"sec": float64(time.Second),
		"min": float64(time.Minute),
	}
	if factor, ok := conversionFactor[unit]; ok {
		return float64(d) / factor, ok
	} else {
		fmt.Printf("[Warning] Unsupported timer unit '%s'\n", unit)
		return -1, !ok
	}
}

// PrintAllTimers prints the elapsed time for all timers
func PrintAllTimers() {
	PrintAllTimersWithUnit("")
}

// PrintAllTimers prints the elapsed time for all timers in the specified unit
func PrintAllTimersWithUnit(unit string) {
	for name := range timers {
		elapsed := ElapsedTime(name)
		if elapsedFloat, ok := ConvertUint(elapsed, unit); ok {
			fmt.Printf("Timer '%s': %.2f %s\n", name, elapsedFloat, unit)
		} else if unit == "" {
			fmt.Printf("Timer '%s': %v\n", name, elapsed)
		} else {
			return
		}
	}
}

// StartTimer starts a timer with a given name
func StartTimer(name string) {
	if !ENABLE {
		return
	}
	if timer, exists := timers[name]; !exists || timer.stopped {
		timers[name] = struct {
			start   time.Time
			elapsed time.Duration
			stopped bool
		}{
			start:   time.Now(),
			elapsed: 0,
			stopped: false,
		}
	} else {
		fmt.Printf("[Warning] timer %s already exist and started\n", name)
	}
}

// StopTimer stops the timer and stores the elapsed time
func StopTimer(name string) {
	if !ENABLE {
		return
	}
	if timer, exists := timers[name]; exists && !timer.stopped {
		timers[name] = struct {
			start   time.Time
			elapsed time.Duration
			stopped bool
		}{
			start:   timer.start,
			elapsed: time.Since(timer.start) + timer.elapsed,
			stopped: true,
		}
	} else {
		fmt.Printf("[Warning] timer %s does not exist or already stopped\n", name)
	}
}

// ElapsedTime returns the elapsed time for a given timer name
func ElapsedTime(name string) time.Duration {
	if !ENABLE {
		return -1
	}
	if timer, exists := timers[name]; exists {
		if !timer.stopped {
			return time.Since(timer.start) + timer.elapsed
		}
		return timer.elapsed
	}
	fmt.Printf("[Warning] timer %s does not exist\n", name)
	return 0
}

// SumElapsedTimes returns the total elapsed time for a list of timer names
func SumElapsedTimes(names []string) time.Duration {
	if !ENABLE {
		return -1
	}
	total := time.Duration(0)
	for _, name := range names {
		total += ElapsedTime(name)
	}
	return total
}

// ResetTimer clears the timer for a given name
func ResetTimer(name string) {
	if !ENABLE {
		return
	}
	delete(timers, name)
}
