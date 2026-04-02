function formatCurrency(value) {
    return `KSh ${Math.round(Number(value || 0)).toLocaleString()}`;
}

function inventoryExperience(payload) {
    return {
        cars: payload.cars ?? [],
        searchQuery: payload.initialQuery ?? "",
        selectedYear: "",
        selectedBodyStyle: "",
        selectedTransmission: "",
        compareIds: [],

        get filteredCars() {
            return this.cars.filter((car) => {
                const matchesSearch = [car.model_name, car.engine_type, car.exterior_color, car.body_style]
                    .join(" ")
                    .toLowerCase()
                    .includes(this.searchQuery.toLowerCase().trim());
                const matchesYear = !this.selectedYear || String(car.year) === String(this.selectedYear);
                const matchesBodyStyle = !this.selectedBodyStyle || car.body_style === this.selectedBodyStyle;
                const matchesTransmission = !this.selectedTransmission || car.transmission === this.selectedTransmission;
                return matchesSearch && matchesYear && matchesBodyStyle && matchesTransmission;
            });
        },

        get comparedCars() {
            return this.compareIds
                .map((id) => this.cars.find((car) => car.id === id))
                .filter(Boolean);
        },

        toggleCompare(carId) {
            if (this.compareIds.includes(carId)) {
                this.compareIds = this.compareIds.filter((id) => id !== carId);
                return;
            }
            if (this.compareIds.length === 2) {
                this.compareIds = [this.compareIds[1], carId];
                return;
            }
            this.compareIds = [...this.compareIds, carId];
        },

        isCompared(carId) {
            return this.compareIds.includes(carId);
        },

        resetFilters() {
            this.searchQuery = "";
            this.selectedYear = "";
            this.selectedBodyStyle = "";
            this.selectedTransmission = "";
        },

        comparisonRows() {
            if (this.comparedCars.length !== 2) {
                return [];
            }
            const [left, right] = this.comparedCars;
            return [
                { label: "Year", left: left.year, right: right.year },
                { label: "Body Style", left: left.body_style, right: right.body_style },
                { label: "Engine", left: left.engine_type, right: right.engine_type },
                { label: "Transmission", left: left.transmission, right: right.transmission },
                { label: "Mileage", left: `${left.mileage_km.toLocaleString()} km`, right: `${right.mileage_km.toLocaleString()} km` },
                { label: "Exterior", left: left.exterior_color, right: right.exterior_color },
                { label: "Horsepower", left: `${left.specs.horsepower} hp`, right: `${right.specs.horsepower} hp` },
                { label: "Torque", left: `${left.specs.torque_nm} Nm`, right: `${right.specs.torque_nm} Nm` },
                { label: "0-100 km/h", left: `${Number(left.specs.zero_to_hundred_s).toFixed(1)}s`, right: `${Number(right.specs.zero_to_hundred_s).toFixed(1)}s` },
                { label: "Price", left: left.price_label, right: right.price_label },
                { label: "Provenance", left: left.certified_provenance ? "Certified" : "Standard", right: right.certified_provenance ? "Certified" : "Standard" },
            ];
        },
    };
}

function vehicleDetailExperience(payload) {
    return {
        car: payload.car ?? { images: [], base_price: 0 },
        activeImageIndex: 0,
        downPaymentRate: 0.1,
        annualRate: 0.089,
        termMonths: 60,

        activeImage() {
            return this.car.images?.[this.activeImageIndex] ?? null;
        },

        scrollToIndex(index) {
            if (!this.car.images?.length) {
                return;
            }

            const boundedIndex = Math.max(0, Math.min(index, this.car.images.length - 1));
            this.activeImageIndex = boundedIndex;

            const track = this.$refs.galleryTrack;
            if (!track) {
                return;
            }

            const slideWidth = track.clientWidth || 1;
            track.scrollTo({
                left: boundedIndex * slideWidth,
                behavior: "smooth",
            });
        },

        syncFromScroll(track) {
            if (!track || !this.car.images?.length) {
                return;
            }

            const slideWidth = track.clientWidth || 1;
            this.activeImageIndex = Math.round(track.scrollLeft / slideWidth);
        },

        scrollGallery(event) {
            const track = this.$refs.galleryTrack;
            if (!track || !this.car.images?.length) {
                return;
            }

            if (Math.abs(event.deltaY) <= Math.abs(event.deltaX)) {
                return;
            }

            event.preventDefault();
            track.scrollBy({
                left: event.deltaY,
                behavior: "smooth",
            });
        },

        nextImage() {
            if (!this.car.images?.length) {
                return;
            }
            this.scrollToIndex((this.activeImageIndex + 1) % this.car.images.length);
        },

        prevImage() {
            if (!this.car.images?.length) {
                return;
            }
            this.scrollToIndex((this.activeImageIndex - 1 + this.car.images.length) % this.car.images.length);
        },

        monthlyPayment() {
            const principal = Number(this.car.base_price || 0) * (1 - this.downPaymentRate);
            const monthlyRate = this.annualRate / 12;
            if (monthlyRate === 0) {
                return principal / this.termMonths;
            }
            return principal * (monthlyRate * (1 + monthlyRate) ** this.termMonths) / (((1 + monthlyRate) ** this.termMonths) - 1);
        },

        formatCurrency,
    };
}

function configuratorExperience(payload) {
    const variants = payload.variants ?? [];
    const wheelOptions = payload.wheelOptions ?? [];

    return {
        car: payload.car ?? { base_price: 0 },
        variants,
        wheelOptions,
        selectedVariantId: variants[0]?.id ?? null,
        selectedWheelId: wheelOptions[0]?.id ?? null,

        get activeVariant() {
            return this.variants.find((variant) => variant.id === this.selectedVariantId) ?? this.variants[0] ?? {};
        },

        get activeWheel() {
            return this.wheelOptions.find((wheel) => wheel.id === this.selectedWheelId) ?? this.wheelOptions[0] ?? {};
        },

        configuredPrice() {
            return Number(this.car.base_price || 0)
                + Number(this.activeVariant.price_delta || 0)
                + Number(this.activeWheel.price_delta || 0);
        },

        formatCurrency,
    };
}
