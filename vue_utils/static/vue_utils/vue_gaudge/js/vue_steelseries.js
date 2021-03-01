const DisplayMultiControl = {
  data() {
    return {
      component: null
    }
  }
  ,
  props: {
    header: {
      type: String,
      default: ''
    }
    ,
    detail: {
      type: String,
      default: ''
    }
    ,
    unit: {
      type: String,
      default: ''
    }
    ,
    decimals: {
      type: Number,
      default:
        2
    }
    ,
    numeric: {
      type: Number,
      default:
        0
    }
    ,
    value: {
      type: String,
      default: ''
    }
    ,
    alt_value: {
      type: String,
      default: ''
    }
    ,
    link_alt_value: {
      type: String,
      default: ''
    }
    ,
    header_visible: {
      type: Boolean,
      default: true
    },
    detail_visible: {
      type: Boolean,
      default: true
    },
    unit_visible: {
      type: Boolean,
      default: true
    },
    width: undefined,
    height: undefined,
    color: steelseries.LcdColor.STANDARD,
  }
  ,
  template: `<canvas ref="canvas">No canvas in your browser...sorry...</canvas>`,
  watch: {
    value(newValue) {
      this.component.setValue(newValue);
    },
    alt_value(newValue) {
      this.component.setAltValue(newValue);
    },
    unit(newValue) {
      this.component.setUnitString(newValue);
    },
    header(newValue) {
      this.component.setLcdTitleStrings(newValue);
    }
  },
  mounted() {
    const configuration = {
      headerString: this.header,
      headerStringVisible: this.header_visible,
      unitString: this.unit,
      unitStringVisible: this.unit_visible,
      detailString: this.detail,
      detailStringVisible: this.detail_visible,
      lcdColor: this.color,
      lcdDecimals: this.decimals,
    }
    if (this.width !== undefined && this.width !== null) {
      configuration['width'] = this.width
    }
    if (this.height !== undefined && this.height !== null) {
      configuration['height'] = this.height
    }

    const component = new steelseries.DisplayMulti(this.$refs.canvas, configuration);
    this.component = component;
    this.component.setValue(this.value);
  }
}

const LedControl = {
  data() {
    return {
      component: null
    }
  }
  ,
  props: {
    active: {
      type: Boolean,
      default: true
    },
    blink: {
      type: Boolean,
      default: false
    },
    size: undefined,
    color: steelseries.LedColor.RED_LED,
  }
  ,
  watch: {
    active(newValue) {
      this.component.setLedOnOff(newValue);
    },
    blink(newValue) {
      this.component.blink(newValue);
    }
  },
  methods: {
    check_value_defined(value) {
      return value !== null && value !== undefined;
    },
  },
  template: `<canvas ref="canvas">No canvas in your browser...sorry...</canvas>`,

  mounted() {
    const configuration = {
      ledColor: this.color,
    }

    if (this.size !== undefined && this.size !== null) {
      configuration['size'] = this.size
    }

    const component = new steelseries.Led(this.$refs.canvas, configuration);
    this.component = component;
    this.component.setLedOnOff(this.active);
    this.component.blink(this.blink)

  }
}

const RadialControl = {
  props: {
    title: {
      type: String,
      default: ''
    }
    ,
    unit: {
      type: String,
      default: ''
    }
    ,
    value: {
      type: Number,
      default:
        0
    }
    ,
    minimal_alarm_value: {
      type: Number,
      default: null
    }
    ,
    maximal_alarm_value: {
      type: Number,
      default:
        null
    }
    ,
    minimal_warning_value: {
      type: Number,
      default:
        null
    }
    ,
    maximal_warning_value: {
      type: Number,
      default:
        null
    }
    ,
    min_value: {
      type: Number,
      default:
        0
    }
    ,
    max_value: {
      type: Number,
      default:
        100
    }
    ,
    minimal_alarm_color: {
      type: String,
      default:
        'rgb(103,9,129)'
    }
    ,
    maximal_alarm_color: {
      type: String,
      default:
        'rgb(126,3,27)'

    }
    ,
    minimal_warning_color: {
      type: String,
      default: 'rgb(82,56,153)'

    }
    ,
    maximal_warning_color: {
      type: String,
      default: 'rgb(221,135,8)'

    },
    normal_zone_color: {
      type: String,
      default: 'rgb(13,138,19)'

    },
    show_normal_zone: {
      type: Boolean,
      default: true
    },
    manual_threshold_rising: {
      type: Boolean,
      default: true
    },
    activate_normal_led: {
      type: Boolean,
      default: true
    },
    threshold_rising_use_warning: {
      type: Boolean,
      default: false
    },
    frame_visible: {
      type: Boolean,
      default: true
    },
    background_visible: {
      type: Boolean,
      default: true
    },
    size: undefined,
    frame_design: undefined,
    pointer_type: undefined,
    gauge_type: undefined,
    background_color: undefined,
  }
  ,
  methods: {
    check_value_defined(value) {
      return value !== null && value !== undefined;
    },
    value_triplet(expression, first_value, second_value, default_value) {
      let result = default_value
      if (Boolean(expression) && expression !== 'false' && this.check_value_defined(first_value)) {
        result = first_value
      } else {
        if (this.check_value_defined(second_value)) {
          result = second_value
        }
      }
      return result
      // return expression && this.check_value_defined(first_value) ? first_value :
      //   this.check_value_defined(second_value)? second_value : default_value
    }

  }
  ,
  data() {
    return {
      radial_component: null,
      internal_value: this.value,
      minRaisingValue: 0,
      maxRaisingValue: 0,
    }
  }
  ,
  computed: {
    value_ex: {
      get() {
        return this.internal_value;
      }
      ,
      set(newValue) {
        this.internal_value = newValue;
        this.radial_component.setValue(newValue);
      }
    }
    ,

    raising_pair() {
      const n_max = this.value_triplet(this.threshold_rising_use_warning, this.maximal_warning_value, this.maximal_alarm_value, this.max_value)
      const m_min = this.value_triplet(this.threshold_rising_use_warning, this.minimal_warning_value, this.minimal_alarm_value, this.min_value)
      return [m_min, n_max]
    },

    form_steelseries() {
      const sections = [];
      if (this.check_value_defined(this.minimal_alarm_value)) {
        sections.push(steelseries.Section(this.min_value, this.minimal_alarm_value, this.minimal_alarm_color))
      }
      if (this.check_value_defined(this.minimal_warning_value)) {
        const min = (this.check_value_defined(this.minimal_alarm_value)) ? this.minimal_alarm_value : this.min_value
        sections.push(steelseries.Section(min, this.minimal_warning_value, this.minimal_warning_color))
      }
      if (this.check_value_defined(this.maximal_warning_value !== undefined)) {
        const max = (this.check_value_defined(this.maximal_alarm_value)) ? this.maximal_alarm_value : this.max_value
        sections.push(steelseries.Section(this.maximal_warning_value, max, this.maximal_warning_color))
      }
      if (this.check_value_defined(this.maximal_alarm_value)) {
        sections.push(steelseries.Section(this.maximal_alarm_value, this.max_value, this.maximal_alarm_color))
      }
      if (this.show_normal_zone && this.show_normal_zone !== 'false') {
        const min = (this.check_value_defined(this.minimal_alarm_value)) ? this.minimal_alarm_value : this.min_value
        const max = (this.check_value_defined(this.maximal_alarm_value)) ? this.maximal_alarm_value : this.max_value
        sections.push(steelseries.Section(min, max, this.normal_zone_color))
      }
      return sections
    }
  }
  ,
  watch: {
    value(newValue) {
      //this.value = newValue; <- Так делать нельзя
      this.radial_component.setValueAnimated(this.value);
      if (this.manual_threshold_rising) {
        const [min, max] = this.raising_pair
        if (this.activate_normal_led) {
          if (newValue < max && newValue > min) {
            this.radial_component.setUserLedOnOff(true)
            this.radial_component.blinkUserLed(true)
          } else {
            this.radial_component.blinkUserLed(false)
            this.radial_component.setUserLedOnOff(false)
          }
        }

        if ((newValue >= max && max < this.radial_component.threshold) || newValue <= min) {
          this.radial_component.setThresholdRising(false);
        } else {
          this.radial_component.setThresholdRising(true);
        }

      }
    }
  }
  ,
  template: `<canvas ref="canvas">No canvas in your browser...sorry...</canvas>`,

  mounted() {
    const configuration = {
      titleString: this.title,
      unitString: this.unit,
      section: this.form_steelseries,
      userLedVisible: true
    }
    if (this.size !== undefined && this.size !== null) {
      configuration['size'] = this.size
    }
    if (this.max_value !== undefined && this.max_value !== null) {
      configuration['maxValue'] = this.max_value;
    }
    if (this.min_value !== undefined && this.min_value !== null) {
      configuration['minValue'] = this.min_value;
    }
    if (this.manual_threshold_rising) {
      configuration['threshold'] = this.max_value
    }

    if (this.check_value_defined(this.frame_design)) {
      configuration['frameDesign'] = this.frame_design
    }
    if (this.check_value_defined(this.pointer_type)) {
      configuration['pointerType'] = this.pointer_type
    }
    if (this.check_value_defined(this.gauge_type)) {
      configuration['gaugeType'] = this.gauge_type
    }
    if (this.check_value_defined(this.background_color)) {
      configuration['backgroundColor'] = this.background_color
    }

    if (this.check_value_defined(this.frame_visible)) {
      configuration['frameVisible'] = this.frame_visible
    }
    if (this.check_value_defined(this.background_visible)) {
      configuration['backgroundVisible'] = this.background_visible
    }
    const [, max] = this.raising_pair
    const component = new steelseries.Radial(this.$refs.canvas, configuration);
    component.setThreshold(max);
    this.radial_component = component;
    this.radial_component.setValue(this.value);

  }
}

const LiniarControl = {
  data() {
    return {
      component: null
    }
  }
  ,
  props: {
    title: {
      type: String,
      default: ''
    }
    ,
    unit: {
      type: String,
      default: ''
    }
    ,
    value: {
      type: Number,
      default:
        0
    }
    ,
    minimal_alarm_value: {
      type: Number,
      default: null
    }
    ,
    maximal_alarm_value: {
      type: Number,
      default:
        null
    }
    ,
    minimal_warning_value: {
      type: Number,
      default:
        null
    }
    ,
    maximal_warning_value: {
      type: Number,
      default:
        null
    }
    ,
    min_value: {
      type: Number,
      default:
        0
    }
    ,
    max_value: {
      type: Number,
      default:
        100
    }
    ,
    minimal_alarm_color: {
      type: String,
      default:
        'rgb(103,9,129)'
    }
    ,
    maximal_alarm_color: {
      type: String,
      default:
        'rgb(126,3,27)'

    }
    ,
    minimal_warning_color: {
      type: String,
      default: 'rgb(82,56,153)'

    }
    ,
    maximal_warning_color: {
      type: String,
      default: 'rgb(221,135,8)'

    },
    normal_zone_color: {
      type: String,
      default: 'rgb(13,138,19)'

    },
    show_normal_zone: {
      type: Boolean,
      default: true
    },
    manual_threshold_rising: {
      type: Boolean,
      default: true
    },
    activate_normal_led: {
      type: Boolean,
      default: true
    },
    threshold_rising_use_warning: {
      type: Boolean,
      default: false
    },
    frame_visible: {
      type: Boolean,
      default: true
    },
    background_visible: {
      type: Boolean,
      default: true
    },
    height: undefined,
    width: undefined,
    frame_design: undefined,
    pointer_type: undefined,
    gauge_type: undefined,
    background_color: undefined,
  }
  ,
  watch: {
    value(newValue) {
      //this.value = newValue; <- Так делать нельзя
      this.component.setValueAnimated(this.value);
      if (this.manual_threshold_rising) {
        const [min, max] = this.raising_pair

        if ((newValue >= max && max < this.component.threshold) || newValue <= min) {
          this.component.setThresholdRising(false);
        } else {
          this.component.setThresholdRising(true);
        }

      }
    }
  }
  ,
  template: `<canvas ref="canvas">No canvas in your browser...sorry...</canvas>`,
  methods: {
    check_value_defined(value) {
      return value !== null && value !== undefined;
    },
    value_triplet(expression, first_value, second_value, default_value) {
      let result = default_value
      if (Boolean(expression) && expression !== 'false' && this.check_value_defined(first_value)) {
        result = first_value
      } else {
        if (this.check_value_defined(second_value)) {
          result = second_value
        }
      }
      return result
      // return expression && this.check_value_defined(first_value) ? first_value :
      //   this.check_value_defined(second_value)? second_value : default_value
    }

  }
  ,
  mounted() {
    const configuration = {
      titleString: this.title,
      unitString: this.unit,
      section: this.form_steelseries,
      userLedVisible: true
    }
    if (this.width !== undefined && this.width !== null) {
      configuration['width'] = this.width
    }
    if (this.height !== undefined && this.height !== null) {
      configuration['height'] = this.height
    }

    if (this.max_value !== undefined && this.max_value !== null) {
      configuration['maxValue'] = this.max_value;
    }
    if (this.min_value !== undefined && this.min_value !== null) {
      configuration['minValue'] = this.min_value;
    }
    if (this.manual_threshold_rising) {
      configuration['threshold'] = this.max_value
    }

    if (this.check_value_defined(this.frame_design)) {
      configuration['frameDesign'] = this.frame_design
    }
    if (this.check_value_defined(this.pointer_type)) {
      configuration['pointerType'] = this.pointer_type
    }
    if (this.check_value_defined(this.gauge_type)) {
      configuration['gaugeType'] = this.gauge_type
    }
    if (this.check_value_defined(this.background_color)) {
      configuration['backgroundColor'] = this.background_color
    }

    if (this.check_value_defined(this.frame_visible)) {
      configuration['frameVisible'] = this.frame_visible
    }
    if (this.check_value_defined(this.background_visible)) {
      configuration['backgroundVisible'] = this.background_visible
    }
    const [, max] = this.raising_pair
    const component = new steelseries.Linear(this.$refs.canvas, configuration);
    component.setThreshold(max);
    this.component = component;
    this.component.setValue(this.value);

  },

  computed: {
    raising_pair() {
      const n_max = this.value_triplet(this.threshold_rising_use_warning, this.maximal_warning_value, this.maximal_alarm_value, this.max_value)
      const m_min = this.value_triplet(this.threshold_rising_use_warning, this.minimal_warning_value, this.minimal_alarm_value, this.min_value)
      return [m_min, n_max]
    },
  }
}

export {RadialControl, LedControl, DisplayMultiControl, LiniarControl};
