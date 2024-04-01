import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { HttpService } from '../services/http.service';
import {CommonModule, NgIf} from '@angular/common';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-leaderboard',
  standalone: true,
  templateUrl: './leaderboard.component.html',
  styleUrls: ['./leaderboard.component.css'],
  imports:[LeaderboardComponent, CommonModule, FormsModule]
})

export class LeaderboardComponent {
  zipcode: string = '';
  leaderboardData: any[] = [];
  selectedOption: string = 'showALL';
  inputted: boolean = false;
  token: any = '';

  constructor(private httpservice: HttpService, private authserivce: AuthService) {}
  
  leaderboard() {
    this.httpservice.leaderboard(this.zipcode)
    .subscribe({
      next: response => {
        console.log(response)
        this.inputted = true
        this.leaderboardData = response
      },
      error: error => console.error('Error!', error)
    });
  }

  executeLeaderboardFunction() {
    switch(this.selectedOption) {
      case 'showAll':
        this.httpservice.leaderboard(this.zipcode)
        .subscribe({
          next: response => {
            console.log(response)
            this.leaderboardData = response
          },
          error: error => console.error('Error!', error)
        });
        break;
      case 'showMonth':
        this.httpservice.monthly_leaderboard(this.zipcode)
        .subscribe({
          next: response => {
            console.log(response)
            this.leaderboardData = response
          },
          error: error => console.error('Error!', error)
        });
        break;
      }
    }

    getToken() {
      if(this.authserivce.isLoggedIn()) {
        this.token = this.authserivce.getToken()
      }
    }
  }
