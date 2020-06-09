// https://maps.googleapis.com/maps/api/place/autocomplete/output?input="mall"&key="AIzaSyDYI4DMOWY-oHQvQ3tesMW0SrdVKu9cN2U"
// http://9c9697b22883.ngrok.io/


const API_KEY = 'AIzaSyACLuoDomujgtH1FgRDALg_eUDdwqDr1cg'

var app = new Vue({
  el: '#app',
  data: {
    loading: false,
    geolocation: false,
    static: {
      tips: {
        walking: [
          'Don\'t forget to always have a mask or face covering. Remember to keep at least six feet physical distance from others.'
        ],
        driving: [
          'If you\'re using ride sharing, for the driver\'s safety, don\'t ride if you feel sick. Even if you\'re healthy, sit in the back to keep some distance between you and the driver. Wash your hands as soon as you can after your ride.',
          'When you drive, you’ll need to refuel. That means you\'ll have to use gas pumps and credit card keypads that other people have touched. Try to wash your hands or use an alcohol-based hand sanitizer',
          'To protect yourself, carry a pair of disposable gloves in your car. Put them on before you pay or pump gas. Or use a disinfecting wipe to clean off the pump handle and keypad. After you finish pumping gas, wash your hands or use an alcohol-based hand sanitizer.'
        ],
        bicycling: [
          'If you opt for a rental bike or e-scooter, carefully wash your hands after each use.',
          'Wipe down your handlebars with a disinfectant before riding.',
          'Consider wearing gloves and washing your hands before and after riding.'
        ],
        transit: [
          'Travel at off-peak times when you can -- like late morning or before evening rush hour. Avoid subway cars and buses packed with people. If you count more than 10-15 passengers on your bus or train, wait for the next one.',
          'If possible, leave an empty seat between you and the next passenger.',
          'Clean your hands as soon as possible after your trip. Surfaces in a public transit setting most likely to harbor the virus are those that are most commonly touched.',
          'Wash your hands as soon as possible after leaving your bus or train. A thorough rub with a hand sanitizer makes sense. Even more important is thorough hand-washing -- 20 seconds with soap and water.',
          'Avoid touching your face with your hands to keep any germs you might have picked up from getting into your system.'
        ]
      },
      activities: {
        indoor: [
          { text: 'Shopping at the mall', value: 'shopping'},
          { text: 'Going to the grocery store', value: 'grocery'},
          { text: 'Going to a place of worship', value: 'worship_center'},
          { text: 'Going to a hair salon / barbershop', value: 'hair_salon'},
          { text: 'Going to a library', value: 'library'},
          { text: 'Going to a museum', value: 'museum'},
          { text: 'Going to an indoor dinner party', value: 'dinner_party'},
          { text: 'Eating indoors at a restaurant', value: 'restaurant_indoor'},
          { text: 'Going to a bar', value: 'bar'},
          { text: 'Going to a doctor/dental office', value: 'doctor'},
          { text: 'Going to a crowded indoor place (gym, concert, casino)', value: 'crowded_indoor'}
        ],
        outdoor: [
          { text: 'Walking', value: 'walking' },
          { text: 'Running', value: 'running' },
          { text: 'Medium / high contact sport (basketball, soccer, bowling, etc.)', value: 'high_contact_sport' },
          { text: 'Low contact sport (tennis, golf, etc.)', value: 'low_contact_sport' },
          { text: 'Going to the park', value: 'park' },
          { text: 'Going to a backyard barbecue', value: 'barbecue' },
          { text: 'Eating outdoors at a restaurant', value: 'restaurant_outdoor' },
          { text: 'Going to a crowded outdoor place (amusement park, beach)', value: 'crowded_outdoor' },
          { text: 'Going to a playground', value: 'playground' },
          { text: 'Swimming at a public pool', value: 'swimming' }
        ]
      },
      transport: [
        { text: 'Driving', value: 'driving' },
        { text: 'Biking', value: 'bicycling' },
        { text: 'Walking', value: 'walking' },
        { text: 'Public Transit', value: 'transit' }
      ],
      conditions: [
        { text: 'Diabetes', value: 'diabetes' },
        { text: 'Hypertension', value: 'hypertension' },
        { text: 'Heart/Lung Disease', value: 'heart_or_lung_disease' }
      ],
      ages: [
        { text: '0-30', value: '0-30' },
        { text: '31-50', value: '31-50' },
        { text: '51-64', value: '51-64' },
        { text: '65+', value: '65+' }
      ]
    },

    displayOuting: true,
    outingDetails: false,
    displayPerson: false,
    personDetails: false,
    displayReport: false,
    activityType: '',
    editing: true,
    activeTip: '',
    flags: [],

    outing: {
      place_name: '',
      place_id: '',
      transport: '',
      activity: '',
    },
    person: {
      origin: {
        lat: 0,
        lng: 0
      },
      conditions: [],
      age_group: ''
    },
    riskLevel: {
      name: '',
      number: ''
    },
    computedRisk: null

  },
  computed: {
    activityName() {
      var text = ''
      var selectedActivity = []
      if (this.outing.activity && this.activityType == 'indoor') {
        selectedActivity = this.static.activities.indoor.filter(function(activity) {
        	return activity.value == app.outing.activity;
        });
        text = selectedActivity[0].text;
      }
      else if (this.outing.activity && this.activityType == 'outdoor') {
        selectedActivity = this.static.activities.outdoor.filter(function(activity) {
          return activity.value == app.outing.activity;
        });
        text = selectedActivity[0].text;
      }
      else {
        text = ''
      }
      return text
    }
  },
  methods: {
    getTip() {
      this.activeTip = ''
      let tip = ''
      switch (this.outing.transport) {
        case 'driving':
          tip = this.static.tips.driving[Math.floor(Math.random() * this.static.tips.driving.length)];
          break;
        case 'walking':
          tip = this.static.tips.walking[Math.floor(Math.random() * this.static.tips.walking.length)];
          break;
        case 'bicycling':
          tip = this.static.tips.bicycling[Math.floor(Math.random() * this.static.tips.bicycling.length)];
          break;
        case 'transit':
          currentTip = this.static.tips.transit[Math.floor(Math.random() * this.static.tips.transit.length)];
          break;
        default:
          tip = ''
      }
      console.log(tip);
      this.activeTip = tip
    },
    calculateRisk() {

    let data = {
      outing: this.outing,
      person: this.person
    }
    axios.post('https://covid-risk-api-3bz32takqa-uw.a.run.app/Risk', data,
      {
        headers: {
          "Authorization": 'romkey_eats_padrones_123'
        }
      })
      .then(response => {
        console.log(response.data);
        this.computedRisk = response.data
        this.checkRisk()
        this.checkFlags()
        this.displayReport = true
      })
      .catch((error) => {
        console.log('error: ' + error)
      });
    },
    submitOuting() {
      this.getTip()
      this.outingDetails = true;
      this.displayOuting = !this.displayOuting;
      this.displayPerson = true
    },
    editOuting() {
      this.displayOuting = !this.displayOuting;
      this.displayPerson = !this.displayOuting;
      this.outingDetails = !this.outingDetails;
      this.editing = true;
      setTimeout(function() { initAutocomplete() }, 300);
    },
    submitPerson() {
      this.personDetails = true;
      this.displayPerson = !this.displayPerson;
      this.editing = false;
    },
    editPerson() {
      this.displayPerson = !this.displayPerson;
      this.editing = true;
    },
    checkRisk() {
      switch (this.computedRisk.risk_level) {
        case 1:
          this.riskLevel.name = "Very Low"
          this.riskLevel.number = "very_low"
          break;
        case 2:
          this.riskLevel.name = "Low"
          this.riskLevel.number = "low"
          break;
        case 3:
          this.riskLevel.name = "Medium"
          this.riskLevel.number = "medium"
          break;
        case 4:
          this.riskLevel.name = "High"
          this.riskLevel.number = "high"
          break;
        case 5:
          this.riskLevel.name = "Very High"
          this.riskLevel.number = "very_high"
          break;
        default:

      }
    },
    checkFlags() {
      for (var i = 0; i < this.computedRisk.flags.length; i++) {
        switch (this.computedRisk.flags[i]) {
          case 'transport':
            this.flags.push('High-risk mode of transportation')
            break;
          case 'activity':
            this.flags.push('High-risk type of activity')
            break;
          case 'persona':
            this.flags.push('Vulnerable individual')
            break;
          default:
        }
      }
    }
  },
  mounted() {}
})

function getLocation() {
  app.loading = true
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(showPosition);
  } else {
    alert("Geolocation is not supported by this browser.");
  }
}

function showPosition(position) {
  app.person.origin.lat = position.coords.latitude
  app.person.origin.lng = position.coords.longitude
  app.geolocation = true
  app.loading = false
  setTimeout(function() { initAutocomplete() }, 300);
}

var placeSearch, autocomplete, geocoder, place_id;

function initAutocomplete() {
  geocoder = new google.maps.Geocoder();
  autocomplete = new google.maps.places.Autocomplete(
      (document.getElementById('autocomplete'))/*,
      {types: ['(cities)']}*/);

  autocomplete.addListener('place_changed', fillInAddress);
}

function fillInAddress() {
  var place = autocomplete.getPlace();
  app.outing.place_id = place.place_id;
  app.outing.place_name = place.name;
}
