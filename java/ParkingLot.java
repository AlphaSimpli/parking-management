import java.util.List;
import java.util.ArrayList;
import java.util.stream.Collectors;

public class ParkingLot {
    private int lotId;
    private String name;
    private int capacity;
    private List<ParkingSlot> slots;

    // Constructor
    public ParkingLot(int lotId, String name, int capacity) {
        this.lotId = lotId;
        this.name = name;
        this.capacity = capacity;
        this.slots = new ArrayList<>();
        initializeSlots();
    }

    private void initializeSlots() {
        for (int i = 1; i <= capacity; i++) {
            slots.add(new ParkingSlot(i));
        }
    }

    // Basic methods
    public boolean occupySlot(int slotId) {
        return slots.stream()
                   .filter(s -> s.getSlotId() == slotId)
                   .findFirst()
                   .map(s -> {
                       s.setOccupied(true);
                       return true;
                   })
                   .orElse(false);
    }

    public boolean freeSlot(int slotId) {
        return slots.stream()
                   .filter(s -> s.getSlotId() == slotId)
                   .findFirst()
                   .map(s -> {
                       s.setOccupied(false);
                       return true;
                   })
                   .orElse(false);
    }

    public List<ParkingSlot> getAvailableSlots() {
        return slots.stream()
                   .filter(s -> !s.isOccupied())
                   .collect(Collectors.toList());
    }

    public List<ParkingSlot> getOccupiedSlots() {
        return slots.stream()
                   .filter(ParkingSlot::isOccupied)
                   .collect(Collectors.toList());
    }

    // Getters and setters
    public int getLotId() { return lotId; }
    public void setLotId(int lotId) { this.lotId = lotId; }
    
    public String getName() { return name; }
    public void setName(String name) { this.name = name; }
    
    public int getCapacity() { return capacity; }
    public void setCapacity(int capacity) { this.capacity = capacity; }
    
    public List<ParkingSlot> getSlots() { return slots; }
    public void setSlots(List<ParkingSlot> slots) { this.slots = slots; }
}

class ParkingSlot {
    private int slotId;
    private boolean isOccupied;

    public ParkingSlot(int slotId) {
        this.slotId = slotId;
        this.isOccupied = false;
    }

    // Getters and setters
    public int getSlotId() { return slotId; }
    public void setSlotId(int slotId) { this.slotId = slotId; }
    
    public boolean isOccupied() { return isOccupied; }
    public void setOccupied(boolean occupied) { isOccupied = occupied; }
}