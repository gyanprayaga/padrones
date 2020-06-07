// https://maps.googleapis.com/maps/api/place/autocomplete/output?input="mall"&key="AIzaSyDYI4DMOWY-oHQvQ3tesMW0SrdVKu9cN2U"

const API_KEY = 'AIzaSyACLuoDomujgtH1FgRDALg_eUDdwqDr1cg'

var app = new Vue({
  el: '#app',
  data: {
    geolocation: false,
    static: {
      activities: [
        { text: 'run', value: 'run' },
        { text: 'eat', value: 'eat' },
        { text: 'sleep', value: 'sleep' }
      ],
      transport: [
        { text: 'drive', value: 'driving' },
        { text: 'bike', value: 'bicycling' },
        { text: 'walk', value: 'walking' },
        { text: 'take public transit', value: 'transit' }
      ],
      conditions: [
        { text: 'Diabetes', value: 'diabetes' },
        { text: 'Hypertension', value: 'hypertension' },
        { text: 'Heart Disease', value: 'heart disease' },
      ],
      ages: [
        { text: '0-18', value: '0-18' },
        { text: '36-50', value: '36-50' },
        { text: '51-75', value: '51-75' },
        { text: '76+', value: '76+' }
      ]
    },

    displayOuting: true,
    outingDetails: false,
    displayPerson: false,
    personDetails: false,
    displayReport: false,
    editing: true,

    outing: {
      place_name: '',
      place_id: '',
      transport: 'driving',
      activity: 'run',
    },
    person: {
      origin: {
        lat: 0,
        lng: 0
      },
      conditions: [],
      age: '36-50'
    },
    riskIndex: {
      name: '',
      color: ''
    }
  },
  methods: {
    calculateRisk() {
      this.displayReport = true;
      this.riskIndex.name = 'Very High';
      this.riskIndex.color = 'red';
    },
    submitOuting() {
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
    }
  },
  mounted() {
  }
})

function getLocation() {
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
