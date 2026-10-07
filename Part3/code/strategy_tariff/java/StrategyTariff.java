import java.util.Arrays;
import java.util.Objects;

public final class StrategyTariff {
    private StrategyTariff() {}

    public interface TariffStrategy {
        double getPrice(int timeIndex);
    }

    public static final class FlatTariff implements TariffStrategy {
        private final double price;

        public FlatTariff(double price) {
            if (price < 0) throw new IllegalArgumentException("price must be non-negative");
            this.price = price;
        }

        @Override
        public double getPrice(int timeIndex) {
            return price;
        }
    }

    public static final class TimeOfUseTariff implements TariffStrategy {
        private final double peakPrice;
        private final double offPeakPrice;
        private final int peakStart;
        private final int peakEnd;

        public TimeOfUseTariff(double peakPrice, double offPeakPrice) {
            this(peakPrice, offPeakPrice, 18, 22);
        }

        public TimeOfUseTariff(double peakPrice, double offPeakPrice, int peakStart, int peakEnd) {
            if (Math.min(peakPrice, offPeakPrice) < 0) {
                throw new IllegalArgumentException("prices must be non-negative");
            }
            if (!(0 <= peakStart && peakStart < peakEnd && peakEnd <= 24)) {
                throw new IllegalArgumentException("peak window must fall within a day");
            }
            this.peakPrice = peakPrice;
            this.offPeakPrice = offPeakPrice;
            this.peakStart = peakStart;
            this.peakEnd = peakEnd;
        }

        @Override
        public double getPrice(int timeIndex) {
            if (timeIndex < 0) throw new IllegalArgumentException("timeIndex must be non-negative");
            int hour = timeIndex % 24;
            return peakStart <= hour && hour < peakEnd ? peakPrice : offPeakPrice;
        }
    }

    public static final class DynamicTariff implements TariffStrategy {
        private final double[] prices;

        public DynamicTariff(double[] prices) {
            if (prices == null || prices.length == 0 || Arrays.stream(prices).anyMatch(price -> price < 0)) {
                throw new IllegalArgumentException("prices must be a non-empty, non-negative series");
            }
            this.prices = Arrays.copyOf(prices, prices.length);
        }

        @Override
        public double getPrice(int timeIndex) {
            if (timeIndex < 0) throw new IllegalArgumentException("timeIndex must be non-negative");
            return prices[timeIndex % prices.length];
        }
    }

    public static final class TariffContext {
        private TariffStrategy strategy;

        public TariffContext(TariffStrategy strategy) {
            setStrategy(strategy);
        }

        public void setStrategy(TariffStrategy strategy) {
            this.strategy = Objects.requireNonNull(strategy, "strategy must not be null");
        }

        public double getPrice(int timeIndex) {
            return strategy.getPrice(timeIndex);
        }
    }
}
