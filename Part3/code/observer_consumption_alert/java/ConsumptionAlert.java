import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashMap;
import java.util.List;
import java.util.Map;
import java.util.Objects;

public final class ConsumptionAlert {
    private ConsumptionAlert() {}

    public static final class ConsumptionEvent {
        private final int timeIndex;
        private final Map<String, Double> byLoad;

        public ConsumptionEvent(int timeIndex, Map<String, Double> byLoad) {
            this.timeIndex = timeIndex;
            this.byLoad = Collections.unmodifiableMap(new LinkedHashMap<>(byLoad));
        }

        public int getTimeIndex() {
            return timeIndex;
        }

        public Map<String, Double> getByLoad() {
            return byLoad;
        }
    }

    public interface ConsumptionObserver {
        void update(ConsumptionEvent event);
    }

    public static final class ConsumptionSubject {
        private final List<ConsumptionObserver> observers = new ArrayList<>();

        public void subscribe(ConsumptionObserver observer) {
            Objects.requireNonNull(observer, "observer must not be null");
            if (!observers.contains(observer)) observers.add(observer);
        }

        public void unsubscribe(ConsumptionObserver observer) {
            if (!observers.remove(observer)) {
                throw new IllegalArgumentException("observer is not subscribed");
            }
        }

        public void notifyObservers(ConsumptionEvent event) {
            for (ConsumptionObserver observer : new ArrayList<>(observers)) {
                observer.update(event);
            }
        }
    }

    public static final class AlertRecord {
        private final int timeIndex;
        private final String loadId;
        private final double consumption;
        private final double threshold;

        public AlertRecord(int timeIndex, String loadId, double consumption, double threshold) {
            this.timeIndex = timeIndex;
            this.loadId = loadId;
            this.consumption = consumption;
            this.threshold = threshold;
        }

        public int getTimeIndex() { return timeIndex; }
        public String getLoadId() { return loadId; }
        public double getConsumption() { return consumption; }
        public double getThreshold() { return threshold; }
    }

    public static final class ConsumptionAlertObserver implements ConsumptionObserver {
        private double threshold;
        private final List<AlertRecord> alerts = new ArrayList<>();

        public ConsumptionAlertObserver() {
            this(10.0);
        }

        public ConsumptionAlertObserver(double threshold) {
            setThreshold(threshold);
        }

        public void setThreshold(double threshold) {
            if (threshold <= 0) throw new IllegalArgumentException("threshold must be positive");
            this.threshold = threshold;
        }

        @Override
        public void update(ConsumptionEvent event) {
            for (Map.Entry<String, Double> entry : event.getByLoad().entrySet()) {
                if (entry.getValue() > threshold) {
                    alerts.add(new AlertRecord(
                        event.getTimeIndex(), entry.getKey(), entry.getValue(), threshold
                    ));
                }
            }
        }

        public List<AlertRecord> snapshot() {
            return Collections.unmodifiableList(new ArrayList<>(alerts));
        }
    }
}
