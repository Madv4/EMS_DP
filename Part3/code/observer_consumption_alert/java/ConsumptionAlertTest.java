import java.util.LinkedHashMap;
import java.util.Map;

public final class ConsumptionAlertTest {
    private static int total = 0;
    private static int passed = 0;

    private static void run(String name, Runnable test) {
        total++;
        try {
            test.run();
            passed++;
        } catch (Throwable error) {
            throw new AssertionError(name + " failed", error);
        }
    }

    private static Map<String, Double> oneLoad(String loadId, double consumption) {
        Map<String, Double> result = new LinkedHashMap<>();
        result.put(loadId, consumption);
        return result;
    }

    private static void runCase(
        double threshold,
        int timeIndex,
        String loadId,
        double gridDraw,
        double renewableDraw,
        int expectedAlertCount,
        double expectedConsumption
    ) {
        ConsumptionAlert.ConsumptionSubject subject = new ConsumptionAlert.ConsumptionSubject();
        ConsumptionAlert.ConsumptionAlertObserver observer =
            new ConsumptionAlert.ConsumptionAlertObserver(threshold);
        subject.subscribe(observer);
        double consumption = gridDraw + renewableDraw;
        if (Math.abs(consumption - expectedConsumption) > 1e-9) {
            throw new AssertionError("consumption mismatch");
        }
        subject.notifyObservers(new ConsumptionAlert.ConsumptionEvent(
            timeIndex, oneLoad(loadId, consumption)
        ));
        if (observer.snapshot().size() != expectedAlertCount) {
            throw new AssertionError("alert count mismatch");
        }
        if (!observer.snapshot().isEmpty()
            && Math.abs(observer.snapshot().get(0).getConsumption() - expectedConsumption) > 1e-9) {
            throw new AssertionError("recorded consumption mismatch");
        }
    }

    public static void main(String[] args) {
        run("CA01", () -> runCase(10.0, 0, "load-a", 5.0, 0.0, 0, 5.0));
        run("CA02", () -> runCase(10.0, 1, "load-a", 7.0, 5.0, 1, 12.0));
        run("CA03", () -> runCase(10.0, 2, "load-a", 10.0, 0.0, 0, 10.0));
        run("CA04", () -> runCase(0.05, 3, "load-b", 0.04, 0.02, 1, 0.06));
        run("CA05", () -> runCase(20.0, 4, "load-c", 12.0, 9.0, 1, 21.0));

        run("duplicate subscription", () -> {
            ConsumptionAlert.ConsumptionSubject subject = new ConsumptionAlert.ConsumptionSubject();
            ConsumptionAlert.ConsumptionAlertObserver observer = new ConsumptionAlert.ConsumptionAlertObserver(10.0);
            subject.subscribe(observer);
            subject.subscribe(observer);
            subject.notifyObservers(new ConsumptionAlert.ConsumptionEvent(5, oneLoad("load-a", 11.0)));
            if (observer.snapshot().size() != 1) throw new AssertionError("duplicate alert");
        });

        run("unsubscribe", () -> {
            ConsumptionAlert.ConsumptionSubject subject = new ConsumptionAlert.ConsumptionSubject();
            ConsumptionAlert.ConsumptionAlertObserver observer = new ConsumptionAlert.ConsumptionAlertObserver(10.0);
            subject.subscribe(observer);
            subject.unsubscribe(observer);
            subject.notifyObservers(new ConsumptionAlert.ConsumptionEvent(6, oneLoad("load-a", 12.0)));
            if (!observer.snapshot().isEmpty()) throw new AssertionError("unexpected alert");
        });

        run("multiple loads", () -> {
            ConsumptionAlert.ConsumptionSubject subject = new ConsumptionAlert.ConsumptionSubject();
            ConsumptionAlert.ConsumptionAlertObserver observer = new ConsumptionAlert.ConsumptionAlertObserver(10.0);
            Map<String, Double> loads = new LinkedHashMap<>();
            loads.put("load-a", 11.0);
            loads.put("load-b", 10.0);
            loads.put("load-c", 12.0);
            subject.subscribe(observer);
            subject.notifyObservers(new ConsumptionAlert.ConsumptionEvent(7, loads));
            if (observer.snapshot().size() != 2) throw new AssertionError("expected two alerts");
            if (!observer.snapshot().get(0).getLoadId().equals("load-a")
                || !observer.snapshot().get(1).getLoadId().equals("load-c")) {
                throw new AssertionError("wrong alerted loads");
            }
        });

        run("zero threshold", () -> {
            try {
                new ConsumptionAlert.ConsumptionAlertObserver(0.0);
                throw new AssertionError("expected error");
            } catch (IllegalArgumentException expected) {}
        });
        run("negative threshold", () -> {
            try {
                new ConsumptionAlert.ConsumptionAlertObserver(-1.0);
                throw new AssertionError("expected error");
            } catch (IllegalArgumentException expected) {}
        });

        System.out.println("Observer tests: " + passed + "/" + total + " passed");
    }
}
