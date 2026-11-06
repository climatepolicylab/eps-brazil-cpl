---
marp: true
theme: default
paginate: true
style: |
  section.image-slide {
    display: grid;
    grid-template-rows: auto minmax(0, 1fr);
    gap: 20px;
    padding: 40px 50px;
  }

  section.image-slide h1 {
    margin: 0;
  }

  section.image-slide p {
    min-height: 0;
    margin: 0;
  }

  section.image-slide p img {
    width: 100%;
    height: 100%;
    object-fit: contain;
    display: block;
  }

  /* SLIDE WITH IMAGE AND NOTE */
  section.image-note-slide {
    display: grid;
    grid-template-areas:
      "title title"
      "image notes";
    grid-template-columns: 72% 28%;
    grid-template-rows: auto 1fr;
    gap: 20px;
  }
  
  section.image-note-slide h1 {
    grid-area: title;
  }
  
  section.image-note-slide > p:first-of-type {
    grid-area: image;
  }
  
  section.image-note-slide h2,
  section.image-note-slide ul {
    grid-area: notes;
  }
  
  section.image-note-slide h2 {
    align-self: start;
    margin-bottom: 0.3em;
  }
  
  section.image-note-slide ul {
    align-self: start;
  }
---

<!-- _class: image-slide -->

# Electricity Generation Capacity

![Description](graph_outputs/electricity_generation_capacity.png)

---

<!-- _class: image-slide -->

![](graph_outputs/total_co2e_emissions.png)

---

<!-- _class: image-note-slide -->

# Process Emissions by Industry

![](graph_outputs/process_emissions_by_industry.png)

::: notes

- Peak around 2050
- Declines under aggressive mitigation
- Strong sensitivity to energy demand

:::

---

<!-- _class: image-note-slide -->

![](graph_outputs/total_co2e_by_sector.png)

- Peak around 2050
- Declines under aggressive mitigation
- Strong sensitivity to energy demand
