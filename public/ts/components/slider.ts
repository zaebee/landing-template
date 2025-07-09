// public/ts/components/slider.ts
import { reapplySadsStyles } from "../modules/sadsManager.js";

const SLIDER_COMPONENT_SELECTOR = '[data-sads-component="image-slider"]';
const SLIDES_CONTAINER_SELECTOR = '[data-sads-element="slides-container"]';
const SLIDE_SELECTOR = '[data-sads-element="slide"]';
const PREV_BUTTON_SELECTOR = '[data-sads-element="nav-prev"]';
const NEXT_BUTTON_SELECTOR = '[data-sads-element="nav-next"]';
const DOTS_CONTAINER_SELECTOR = '[data-sads-element="nav-dots"]';
const DOT_SELECTOR = '[data-sads-element="nav-dot"]';

class ImageSlider {
  private sliderElement: HTMLElement;
  private slidesContainer: HTMLElement;
  private slides: HTMLElement[];
  private prevButton: HTMLButtonElement | null;
  private nextButton: HTMLButtonElement | null;
  private dotsContainer: HTMLElement | null;
  private dots: HTMLButtonElement[];

  private currentIndex: number = 0;
  private totalSlides: number = 0;

  constructor(sliderElement: HTMLElement) {
    this.sliderElement = sliderElement;
    this.slidesContainer = sliderElement.querySelector<HTMLElement>(
      SLIDES_CONTAINER_SELECTOR
    ) as HTMLElement;
    this.slides = Array.from(
      sliderElement.querySelectorAll<HTMLElement>(SLIDE_SELECTOR)
    );
    this.prevButton =
      sliderElement.querySelector<HTMLButtonElement>(PREV_BUTTON_SELECTOR);
    this.nextButton =
      sliderElement.querySelector<HTMLButtonElement>(NEXT_BUTTON_SELECTOR);
    this.dotsContainer = sliderElement.querySelector<HTMLElement>(
      DOTS_CONTAINER_SELECTOR
    );
    this.dots = this.dotsContainer
      ? Array.from(
          this.dotsContainer.querySelectorAll<HTMLButtonElement>(DOT_SELECTOR)
        )
      : [];

    this.totalSlides = this.slides.length;
    this.autoplayEnabled = sliderElement.dataset.sadsAutoplay === "true";
    this.autoplayInterval = parseInt(
      sliderElement.dataset.sadsAutoplayInterval || "5000",
      10
    );
    this.autoplayTimerId = null;

    this.init();
  }

  private autoplayEnabled: boolean;
  private autoplayInterval: number;
  private autoplayTimerId: number | null;

  private init(): void {
    if (this.totalSlides === 0) {
      console.warn("Slider initialized with no slides.", this.sliderElement);
      if (this.prevButton) this.prevButton.style.display = "none";
      if (this.nextButton) this.nextButton.style.display = "none";
      if (this.dotsContainer) this.dotsContainer.style.display = "none";
      return;
    }

    if (this.totalSlides <= 1) {
      if (this.prevButton) this.prevButton.style.display = "none";
      if (this.nextButton) this.nextButton.style.display = "none";
      if (this.dotsContainer) this.dotsContainer.style.display = "none";
      this.autoplayEnabled = false; // No point in autoplaying one slide
    } else {
      if (this.prevButton) {
        this.prevButton.addEventListener("click", () => {
          this.showPrevSlide();
          this.resetAutoplay();
        });
      }
      if (this.nextButton) {
        this.nextButton.addEventListener("click", () => {
          this.showNextSlide();
          this.resetAutoplay();
        });
      }
      this.dots.forEach((dot, index) => {
        dot.addEventListener("click", () => {
          this.showSlide(index);
          this.resetAutoplay();
        });
      });

      if (this.autoplayEnabled) {
        this.sliderElement.addEventListener("mouseenter", () =>
          this.pauseAutoplay()
        );
        this.sliderElement.addEventListener("mouseleave", () =>
          this.startAutoplay()
        );
        this.sliderElement.addEventListener("focusin", () =>
          this.pauseAutoplay()
        ); // Pause if user tabs into slider elements
        this.sliderElement.addEventListener("focusout", () =>
          this.startAutoplay()
        ); // Resume if focus leaves slider
      }
    }

    // Ensure slides container is wide enough to hold all slides if we were to use transform: translateX
    // For display:none/flex, this is not strictly necessary but doesn't harm.
    // this.slidesContainer.style.width = `${this.totalSlides * 100}%`;
    // this.slides.forEach(slide => {
    //     slide.style.width = `${100 / this.totalSlides}%`; // Each slide takes up its portion of the container
    // });

    this.showSlide(0); // Show the first slide initially
    if (this.autoplayEnabled) {
      this.startAutoplay();
    }
  }

  private startAutoplay(): void {
    if (!this.autoplayEnabled || this.autoplayTimerId !== null) return;
    this.autoplayTimerId = setInterval(() => {
      this.showNextSlide();
    }, this.autoplayInterval);
  }

  private pauseAutoplay(): void {
    if (!this.autoplayEnabled || this.autoplayTimerId === null) return;
    clearInterval(this.autoplayTimerId);
    this.autoplayTimerId = null;
  }

  private resetAutoplay(): void {
    if (!this.autoplayEnabled) return;
    this.pauseAutoplay();
    this.startAutoplay();
  }

  private showSlide(index: number): void {
    if (index < 0 || index >= this.totalSlides) {
      console.warn(`Invalid slide index: ${index}`);
      return;
    }

    this.currentIndex = index;

    // Simple show/hide logic (can be replaced with transform for sliding effect)
    this.slides.forEach((slide, i) => {
      slide.setAttribute(
        "data-sads-display",
        i === this.currentIndex ? "flex" : "none"
      );
      // Update ARIA attributes for accessibility
      slide.setAttribute(
        "aria-hidden",
        i === this.currentIndex ? "false" : "true"
      );
      const img = slide.querySelector<HTMLImageElement>(
        '[data-sads-element="slide-image"]'
      );
      if (img) {
        img.setAttribute("tabindex", i === this.currentIndex ? "0" : "-1");
      }
    });

    // Update slide container position (for simple sliding effect, not needed for display:none/flex)
    // this.slidesContainer.style.transform = `translateX(-${this.currentIndex * (100 / this.totalSlides)}%)`;

    if (this.dots.length === this.totalSlides) {
      this.dots.forEach((dot, i) => {
        if (i === this.currentIndex) {
          dot.setAttribute("data-sads-active", "true");
          dot.setAttribute("aria-current", "true");
          // SADS attributes for active dot styling (e.g., different background)
          dot.setAttribute("data-sads-bg-color", "text-accent");
        } else {
          dot.removeAttribute("data-sads-active");
          dot.removeAttribute("aria-current");
          dot.setAttribute("data-sads-bg-color", "neutral-subtle");
        }
      });
    }

    if (this.prevButton) {
      this.prevButton.disabled = this.currentIndex === 0;
      this.prevButton.setAttribute(
        "data-sads-opacity",
        this.currentIndex === 0 ? "custom:0.5" : "custom:1"
      );
    }
    if (this.nextButton) {
      this.nextButton.disabled = this.currentIndex === this.totalSlides - 1;
      this.nextButton.setAttribute(
        "data-sads-opacity",
        this.currentIndex === this.totalSlides - 1 ? "custom:0.5" : "custom:1"
      );
    }

    // Important: Reapply SADS styles after changing attributes that affect styling
    reapplySadsStyles();
  }

  public showNextSlide(): void {
    const nextIndex = (this.currentIndex + 1) % this.totalSlides;
    this.showSlide(nextIndex);
  }

  public showPrevSlide(): void {
    const prevIndex =
      (this.currentIndex - 1 + this.totalSlides) % this.totalSlides;
    this.showSlide(prevIndex);
  }
}

export function initSliderComponent(): void {
  const sliderElements = document.querySelectorAll<HTMLElement>(
    SLIDER_COMPONENT_SELECTOR
  );
  if (sliderElements.length > 0) {
    sliderElements.forEach((sliderEl) => new ImageSlider(sliderEl));
    console.log(
      `Image Slider Component(s) Initialized: ${sliderElements.length} found.`
    );
  }
}
