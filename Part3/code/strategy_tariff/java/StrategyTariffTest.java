public final class StrategyTariffTest {
    private static int total = 0;
    private static int passed = 0;
    private static final StrategyTariff.TariffContext CONTEXT =
        new StrategyTariff.TariffContext(new StrategyTariff.FlatTariff(0.15));

    private static void run(String name, Runnable test) {
        total++;
        try {
            test.run();
            passed++;
        } catch (Throwable error) {
            throw new AssertionError(name + " failed", error);
        }
    }

    private static void checkPrice(
        StrategyTariff.TariffStrategy strategy,
        int timeIndex,
        double expected
    ) {
        CONTEXT.setStrategy(strategy);
        double actual = CONTEXT.getPrice(timeIndex);
        if (Math.abs(actual - expected) > 1e-9) {
            throw new AssertionError("expected " + expected + ", got " + actual);
        }
    }

    private static void expectError(Runnable action) {
        try {
            action.run();
        } catch (IllegalArgumentException expected) {
            return;
        }
        throw new AssertionError("expected IllegalArgumentException");
    }

    public static void main(String[] args) {
        run("DT01", () -> checkPrice(new StrategyTariff.FlatTariff(0.15), 0, 0.15));
        run("DT02", () -> checkPrice(new StrategyTariff.FlatTariff(0.15), 23, 0.15));
        run("DT03", () -> checkPrice(new StrategyTariff.TimeOfUseTariff(0.30, 0.15, 18, 22), 17, 0.15));
        run("DT04", () -> checkPrice(new StrategyTariff.TimeOfUseTariff(0.30, 0.15, 18, 22), 18, 0.30));
        run("DT05", () -> checkPrice(new StrategyTariff.TimeOfUseTariff(0.30, 0.15, 18, 22), 21, 0.30));
        run("DT06", () -> checkPrice(new StrategyTariff.TimeOfUseTariff(0.30, 0.15, 18, 22), 22, 0.15));
        run("DT07", () -> checkPrice(new StrategyTariff.TimeOfUseTariff(0.30, 0.15, 18, 22), 42, 0.30));
        run("DT08", () -> checkPrice(new StrategyTariff.DynamicTariff(new double[] {0.10, 0.20, 0.35, 0.15}), 0, 0.10));
        run("DT09", () -> checkPrice(new StrategyTariff.DynamicTariff(new double[] {0.10, 0.20, 0.35, 0.15}), 2, 0.35));
        run("DT10", () -> checkPrice(new StrategyTariff.DynamicTariff(new double[] {0.10, 0.20, 0.35, 0.15}), 4, 0.10));
        run("negative flat price", () -> expectError(() -> new StrategyTariff.FlatTariff(-0.01)));
        run("negative time-of-use price", () -> expectError(() -> new StrategyTariff.TimeOfUseTariff(-0.01, 0.10)));
        run("invalid peak window", () -> expectError(() -> new StrategyTariff.TimeOfUseTariff(0.30, 0.15, 22, 18)));
        run("empty dynamic series", () -> expectError(() -> new StrategyTariff.DynamicTariff(new double[] {})));
        run("negative dynamic price", () -> expectError(() -> new StrategyTariff.DynamicTariff(new double[] {0.10, -0.20})));
        run("negative time-of-use index", () -> expectError(() -> new StrategyTariff.TimeOfUseTariff(0.30, 0.15).getPrice(-1)));
        run("negative dynamic index", () -> expectError(() -> new StrategyTariff.DynamicTariff(new double[] {0.10}).getPrice(-1)));
        System.out.println("Strategy tests: " + passed + "/" + total + " passed");
    }
}
